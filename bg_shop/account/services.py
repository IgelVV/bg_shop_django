from typing import TypeVar, Optional
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.views import LoginView


from django.db import utils


UserType = TypeVar('UserType', bound=AbstractBaseUser)
User: UserType = get_user_model()


class AccountService:
    @staticmethod
    def register_user(**fields) -> Optional[UserType]:
        try:
            return User.objects.create_user(**fields)
        except utils.IntegrityError:
            return None

    def authenticate(self, user:UserType) -> None:
        ...
