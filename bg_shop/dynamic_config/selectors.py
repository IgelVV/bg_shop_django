from typing import Any
from django.contrib.auth import get_user_model

from dynamic_config import models


class AdminConfigSelector:  # todo cache
    @staticmethod
    def get_config(key: str) -> Any:
        config = models.DynamicConfig.objects.get(pk=1)
        if hasattr(config, key):
            return getattr(config, key)
        else:
            raise KeyError(f"DynamicConfig has no attribute `{key}`.")

    @property
    def boundary_of_free_delivery(self):
        return self.get_config(key="boundary_of_free_delivery")
