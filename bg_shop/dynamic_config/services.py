from typing import Any
from django.contrib.auth import get_user_model

from dynamic_config import models


User = get_user_model()


class AdminConfigService:
    def get_config(self, key: str) -> Any:
        ...
