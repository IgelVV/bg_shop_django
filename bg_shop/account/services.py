from typing import TypeVar, Optional, Any, Dict
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from django.db import utils

from account.models import Profile
from common.models import Image

UserType = TypeVar('UserType', bound=AbstractUser)
User: UserType = get_user_model()


class AccountService:
    @staticmethod
    @transaction.atomic
    def register_user(
            username: str,
            password: str,
            **extra_fields
    ) -> Optional[UserType]:
        """
        
        :param username: 
        :param password: 
        :param extra_fields: 
        :return: 
        """
        try:
            user = User.objects.create_user(username, password, **extra_fields)
        except utils.IntegrityError:
            return None
        Profile(user=user)
        return user

    @staticmethod
    def change_password(user: UserType, password: str) -> None:
        """
        
        :param user: 
        :param password: 
        :return: 
        """
        is_old = user.check_password(password)
        if is_old:
            raise ValueError("The new password matches the old one")
        user.set_password(password)

    @transaction.atomic
    def update_avatar(self, user: UserType, avatar: UploadedFile) -> None:
        """
        Creates new Image and binds with user's profile. Deletes previous
        avatar.
        :param user: 
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
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.clean_fields()
        user.save()
        profile = self.get_or_create_profile(user=user)
        profile.phone_number = phone
        profile.clean_fields()
        profile.save()
