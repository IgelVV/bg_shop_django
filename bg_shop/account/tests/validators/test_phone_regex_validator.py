from django.test import TestCase
from django.core import exceptions

from account import validators


class PhoneRegexValidatorTestCase(TestCase):
    def test_correct_phone(self):
        phone = "0123456789"
        validators.PhoneRegexValidator().__call__(phone)

    def test_not_only_digits(self):
        phone = "phone56789"
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Not only digits are acceptable.",
        ):
            validators.PhoneRegexValidator().__call__(phone)

    def test_too_long(self):
        phone = "01234567890"
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Too long password is acceptable.",
        ):
            validators.PhoneRegexValidator().__call__(phone)

    def test_too_short(self):
        phone = "012345678"
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Too short password is acceptable.",
        ):
            validators.PhoneRegexValidator().__call__(phone)
