from django.test import TestCase
from django.core import exceptions

from common import validators


class FileMaxSizeValidatorTestCase(TestCase):
    class FileMock:
        def __init__(self, size, name):
            self.size = size
            self.name = name

    class FieldFileMock:
        def __init__(self, size, name):
            self.file = FileMaxSizeValidatorTestCase.FileMock(size, name)

    def test_raise_error_if_file_too_big(self):
        validator = validators.FileMaxSizeValidator(
            limit_value=1,
            message="max size"
        )
        field_file = self.FieldFileMock(2, "test")
        with self.assertRaises(
                exceptions.ValidationError,
                msg="Wrong validation."
        ) as cm:
            validator(field_file)
        self.assertIn("max size", cm.exception.message, "Wrong message.")

    def test_pass_validation_if_size_less_or_equal_than_limit(self):
        validator = validators.FileMaxSizeValidator(
            limit_value=1,
            message="max size"
        )
        field_file = self.FieldFileMock(1, "test")
        try:
            validator(field_file)
        except exceptions.ValidationError:
            raise AssertionError(
                "Validator rises Validation error with correct value.")
