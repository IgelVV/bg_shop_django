from typing import TypeVar, Optional
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.views import LoginView


from django.db import utils


UserType = TypeVar('UserType', bound=AbstractBaseUser)
User: UserType = get_user_model()


class AccountService:
    @staticmethod
    def register_user(
            username: str,
            password: str,
            **extra_fields
    ) -> Optional[UserType]:
        try:
            return User.objects.create_user(username, password, **extra_fields)
        except utils.IntegrityError:
            return None

    @staticmethod
    def change_password(user: UserType, password: str) -> None:
        is_old = user.check_password(password)
        if is_old:
            raise ValueError("The new password matches the old one")
        user.set_password(password)
