from django.core.validators import RegexValidator


class PhoneRegexValidator(RegexValidator):
    def __int__(self, message: str):
        super().__init__(regex=r'^d{10}$', message=message)
