from random import choices
from string import ascii_letters, digits

from django.test import TestCase

from account import serializers


class ValidatePasswordTestCase(TestCase):
    def test_too_long_password(self):
        password = "".join(
            choices(ascii_letters + digits, k=129))
        serializer = serializers.PasswordSerializer(
            data={"password": password},
        )
        self.assertFalse(
            serializer.is_valid(), "Too long password is acceptable.")
        self.assertEqual(set(serializer.errors), {'password'}, "Wrong error.")

    def test_validate_password_returns_value(self):
        password = "Strong123Password_"
        serializer = serializers.PasswordSerializer(
            data={"password": password},
        )
        serializer.is_valid()
        self.assertEqual(
            serializer.validated_data["password"],
            password,
            "Wrong error.",
        )
