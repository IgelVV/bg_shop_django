from typing import TypeVar

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from account import models

UserType = TypeVar('UserType', bound=AbstractUser)
User = get_user_model()


class AccountSelector:
    def get_account_data(self, user: UserType) -> dict[str, str]:
        return dict(  # todo
            fullName="",
            email="",
            phone="",
            avatar="",
        )
