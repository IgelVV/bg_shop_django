from django.core.exceptions import ValidationError
from django.test import TestCase
from payment.validators import PaymentNumberRegexValidator


class PaymentNumberRegexValidatorTestCase(TestCase):
    def test_valid_payment_number(self):
        validator = PaymentNumberRegexValidator("Invalid payment number")
        valid_payment_numbers = ["12345678", "87654321", "00000000"]

        for payment_number in valid_payment_numbers:
            try:
                validator(payment_number)
            except ValidationError:
                self.fail(
                    f"Validator raised an exception "
                    f"for a valid payment number: {payment_number}")

    def test_invalid_payment_number(self):
        validator = PaymentNumberRegexValidator("Invalid payment number")
        invalid_payment_numbers = ["123", "abcdefgh", "876543210",
                                   "12 345 678"]

        for payment_number in invalid_payment_numbers:
            with self.assertRaises(ValidationError) as context:
                validator(payment_number)

            self.assertEqual(context.exception.messages[0],
                             "Invalid payment number")
