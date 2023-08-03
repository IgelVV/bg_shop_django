from django.test import TestCase
from django.conf import settings

from dynamic_config import models, services


class SetDefaultConfigTestCase(TestCase):
    def get_config_instance(self):
        return models.DynamicConfig.objects.first()

    def test_set_default_if_instance_is_deleted(self):
        config = self.get_config_instance()
        config.delete()

        services.DynamicConfigService().set_default_config()
        self.assertEqual(
            self.get_config_instance().company_info,
            settings.COMPANY_INFO,
            "Default config value is not set."
        )

    def test_roll_back_changes(self):
        config = self.get_config_instance()
        config.company_info = "test company info"
        config.save()

        services.DynamicConfigService().set_default_config()
        self.assertEqual(
            self.get_config_instance().company_info,
            settings.COMPANY_INFO,
            "Default config value is not set."
        )
