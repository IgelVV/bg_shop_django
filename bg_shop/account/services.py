from typing import TypeVar, Optional
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile


from django.db import utils

from account.models import Profile
from common.models import Image

UserType = TypeVar('UserType', bound=AbstractUser)
User: UserType = get_user_model()


class AccountService:
    @staticmethod
    def register_user(
            username: str,
            password: str,
            **extra_fields
    ) -> Optional[UserType]:
        """Creates new User and Profile"""
        try:
            user = User.objects.create_user(username, password, **extra_fields)
        except utils.IntegrityError:
            return None
        Profile(user=user)
        return user

    @staticmethod
    def change_password(user: UserType, password: str) -> None:
        is_old = user.check_password(password)
        if is_old:
            raise ValueError("The new password matches the old one")
        user.set_password(password)

    @staticmethod
    def update_avatar(user: UserType, avatar: UploadedFile) -> None:
        """
        Creates new Image and binds with user's profile. Deletes previous
        avatar.
        :param user: user model
        :param avatar: Image
        :return: None
        """
        image = Image(img=avatar, description=user.get_username())
        image.save()
        if not hasattr(user, "profile"):
            Profile(user=user)
        # todo delete previous avatar (from storage too) due image service
        user.profile.avatar = image
        user.profile.save()
