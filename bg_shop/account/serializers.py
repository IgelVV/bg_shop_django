"""
Here are only reusable serializers,
other ones are nested into ApiViews directly.
"""

from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core import exceptions


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        """Validates password"""
        password = data.get('password')
        errors = dict()
        try:
            password_validation.validate_password(
                password=password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise exceptions.ValidationError(errors)
        return super().validate(data)
