"""Methods for getting info from db."""

from typing import TypeVar, Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from account import models, services
from common.models import Image

UserType = TypeVar('UserType', bound=AbstractUser)
User = get_user_model()


class AccountSelector:
    """For getting User and Profile info."""

    def get_account_data(self, user: UserType) -> dict[str, Any]:
        """
        Provide data from User model, and related Profile model.

        If there is no related Profile, creates one.
        It is expected that the data will be validated in Api view
        by serializer, so the data can contain extra or optional fields.
        :param user: user obj
        :return: dictionary with fields
        """
        profile: models.Profile = \
            services.AccountService().get_or_create_profile(user=user)
        data = {
            'fullName': user.get_full_name(),
            'email': user.email,
            'phone': profile.phone_number,
            'avatar': self.get_avatar_data(profile)
        }
        return data

    @staticmethod
    def get_avatar_data(profile: models.Profile) -> Optional[dict[str, Any]]:
        """
        Provide json-like data for api.

        :param profile: Profile obj
        :return: dict with renamed fields of Image
        """
        avatar: Image = profile.avatar
        if (avatar is not None) and (avatar.pk is not None):
            return {
                'src': avatar.img.url,
                'alt': avatar.description
            }
