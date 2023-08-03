"""
Here are only reusable serializers.

Other ones are nested into ApiViews directly.
"""

from rest_framework import serializers
from django.contrib.auth import password_validation


class PasswordSerializer(serializers.Serializer):
    """Provides a validation for password."""

    password = serializers.CharField(max_length=128)

    def validate_password(self, value):
        """
        Validate password using django.

        :param value:
        :return:
        """
        password_validation.validate_password(
            password=value)
        return value
