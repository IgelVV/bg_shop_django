from django.core.validators import RegexValidator


class PaymentNumberRegexValidator(RegexValidator):
    def __int__(self, message: str):
        super().__init__(regex=r'^d{8}$', message=message)
