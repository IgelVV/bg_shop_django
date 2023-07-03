"""Main business logic related to User and Profile models."""

from typing import TypeVar, Optional, Any, Dict
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model, login
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from rest_framework import request as drf_request

from django.db import utils

from account.models import Profile
from common.models import Image
from orders import services as order_services

UserType = TypeVar('UserType', bound=AbstractUser)
User: UserType = get_user_model()


# todo учитывать что пользователь может быть is_active=False
class AccountService:
    """To change User and profile data."""

    @staticmethod
    @transaction.atomic
    def register_user(
            username: str,  # todo validation of username (it is possible to set any symbols)
            password: str,  # todo validate password (sets any password)
            **extra_fields
    ) -> Optional[UserType]:
        """
        Try to create user, if it already exists returns None.

        If new user created, also creates Profile.
        :param username: str
        :param password: str
        :param extra_fields: declared in the User model
        :return: created User obj or None if already exist
        """
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                **extra_fields
            )
        except utils.IntegrityError:
            return None
        Profile(user=user)
        return user

    @staticmethod
    def change_password(user: UserType, password: str) -> None:
        # todo perform validation in
        """
        Change user password, it is prohibited to set the same password.

        It is possible to set any password,
        so the password should be validated.
        :param user: the user who changes password
        :param password: already valid password
        :return: None
        """
        is_old = user.check_password(password)
        if is_old:
            raise ValueError("The new password matches the old one")
        user.set_password(password)

    @transaction.atomic
    def update_avatar(self, user: UserType, avatar: UploadedFile) -> None:
        """
        Create new Image and binds with user's profile.

        Deletes previous avatar.
        :param user: User obj
        :param avatar: Image
        :return: None
        """
        description = f"{user.get_username()} avatar"
        image = Image(img=avatar, description=description)
        image.save()
        profile = self.get_or_create_profile(user=user)
        # todo delete previous avatar (from storage too) due image service
        profile.avatar = image
        profile.save()

    @staticmethod
    def get_or_create_profile(
            user: UserType, commit: bool = True) -> Profile:
        """
        Use to get profile that related to user.

        The preferred way to create.
        If commit is False, returns unsaved model to fill and save later.
        empty profile.
        :param user: User obj to bind new Profile or get from
        :param commit: if is True, hits the database,
        if False, Profile needs to be saved later.
        :return:
        """
        if hasattr(user, "profile"):
            profile = user.profile
        else:
            profile = Profile(user=user)
            if commit:
                profile.save()
        return profile

    @transaction.atomic
    def update_account(
            self,
            user: UserType,
            first_name: str,
            last_name: str,
            email: str,
            phone: str,
            avatar: Optional[Dict[str, Any]],  # todo handle `avatar`: None (when avatar is deleted and isn't replased)
            **kwargs,
    ) -> None:
        """
        Change User model and related Profile.

        If avatar = None, deletes Image that is related to profile,
        otherwise does nothing with avatar field.
        :param user:
        :param first_name:
        :param last_name:
        :param email:
        :param phone:
        :param avatar: is None, deletes Image that is related to profile,
        otherwise does nothing
        :param kwargs: optional fields that sre ignored
        :return:
        """
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.full_clean()
        user.save()
        profile = self.get_or_create_profile(user=user)
        profile.phone_number = phone
        profile.full_clean()
        profile.save()

    def login(
            self,
            request: drf_request.Request,
            user: UserType,
            *args,
            **kwargs
    ) -> None:
        """
        Do log-in.

        Transfer cart from anonymous session to new one
        when user is logging in.
        :param request:
        :param user:
        :param args:
        :param kwargs:
        :return:
        """
        cart_service = order_services.CartService(request=request)
        anonymous_cart = cart_service.cart
        login(*args, request=request, user=user, **kwargs,)
        cart_service.merge_carts(session_cart=anonymous_cart)
