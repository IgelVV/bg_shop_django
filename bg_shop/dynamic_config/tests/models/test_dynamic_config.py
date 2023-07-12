from django.db import transaction
from django.test import TestCase
from django.db.utils import IntegrityError

from dynamic_config import models


class DynamicConfigModelTestCase(TestCase):
    def setUp(self) -> None:
        self.instance = models.DynamicConfig.objects.get(pk=1)

    def tearDown(self) -> None:
        self.instance.save()

    def test_recreate_single_object(self):
        self.instance.delete()
        self.instance.save()
        self.assertEqual(
            models.DynamicConfig.objects.first().pk,
            1,
            "Recreated singleton object must have pk=1"
        )

    def test_create_second_object(self):
        self.assertEqual(models.DynamicConfig.objects.count(), 1)
        with self.assertRaises(
                IntegrityError,
                msg="Singleton must have only one instance with pk=1.",
        ):
            with transaction.atomic():
                new_config = models.DynamicConfig(company_info="test")
                new_config.save(force_insert=True)

        self.assertEqual(
            models.DynamicConfig.objects.count(),
            1,
            "Singleton can't have more than one instance."
        )

    def test_update(self):
        test_main_email = "test@mail.com"
        self.instance.main_email = test_main_email
        self.instance.save()
        self.assertEqual(
            models.DynamicConfig.objects.first().main_email,
            test_main_email,
            "Changes are not applied."
        )
        self.assertEqual(
            models.DynamicConfig.objects.count(),
            1,
            "Singleton can't have more than one instance."
        )