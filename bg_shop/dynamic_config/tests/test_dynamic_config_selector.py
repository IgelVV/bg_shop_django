from django.test import TestCase
from django.conf import settings

from dynamic_config import selectors


class GetConfigTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.DynamicConfigSelector()

    def test_get_existing_attribute(self):
        result = self.selector.get_config(key="ordinary_delivery_cost")
        self.assertEqual(
            result, settings.ORDINARY_DELIVERY_COST, "Wrong value.")

    def test_get_wrong_attribute(self):
        with self.assertRaises(
                KeyError,
                msg="A non-existent attribute is accepted."
        ):
            self.selector.get_config(key="non-existent_attribute")
