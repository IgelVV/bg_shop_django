from typing import Any

from dynamic_config import models


class DynamicConfigSelector:  # todo cache delete cache post_save _signal
    def get_instance(self):
        if not hasattr(self, "config"):
            self.config = models.DynamicConfig.objects.get(pk=1)
        return self.config

    def get_config(self, key: str) -> Any:
        """
        Returns value of one of DynamicConfig's fields by key.
        :param key: a name of field in DynamicConfig
        :return: value of the field
        """
        self.get_instance()
        if hasattr(self.config, key):
            return getattr(self.config, key)
        else:
            raise KeyError(f"DynamicConfig has no attribute `{key}`.")

    @property
    def boundary_of_free_delivery(self):
        """
        Shortcut.
        :return: value of `boundary_of_free_delivery` field.
        """
        self.get_instance()
        return self.get_config(key="boundary_of_free_delivery")

    @property
    def ordinary_delivery_cost(self):
        """
        Shortcut.
        :return: value of `ordinary_delivery_cost` field.
        """
        self.get_instance()
        return self.get_config(key="ordinary_delivery_cost")

    @property
    def express_delivery_extra_charge(self):
        """
        Shortcut.
        :return: value of `express_delivery_extra_charge` field.
        """
        self.get_instance()
        return self.get_config(key="express_delivery_extra_charge")
