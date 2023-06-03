from django.core import validators
from django.utils.translation import gettext_lazy as _


class PhoneRegexValidator(validators.RegexValidator):
    regex = r'^\d{10}$'
    message = _(
        "Enter a valid phone. This value must contain 10 digits, "
    )
