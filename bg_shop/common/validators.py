"""Custom validators for common app."""

from django.core import validators
from django.utils.translation import gettext_lazy as _


class FileMaxSizeValidator(validators.BaseValidator):
    """Limit max file (or image) size."""

    message = _("Max file size is %(limit_value)sB")
    code = "max_file_size"

    def compare(self, cleaned, limit_value):
        return cleaned > limit_value

    def clean(self, value):
        return value.file.size
