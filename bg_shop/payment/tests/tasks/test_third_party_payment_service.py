from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from payment.tasks import third_party_payment_service
from payment.enums import PaymentStatuses


class ThirdPartyPaymentServiceTestCase(TestCase):
    @patch("requests.post")
    def test_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": PaymentStatuses.SUCCESS.value
        }
        order_id = 1
        card_number = "12345678"
        payment = Decimal("100.00")

        third_party_payment_service(
            url="http://example.com/api/payment/webhook/",
            order_id=order_id,
            card_number=card_number,
            payment=payment,
        )
        expected_body = {
            "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE,
            "order_id": order_id,
            "status": PaymentStatuses.SUCCESS.value,
            "errors": [],
            "payment_id": f"{order_id}test_payment_id",
        }
        fake_url = "http://app:8000/api/payment/webhook/"
        mock_post.assert_called_once_with(
            fake_url,
            json=expected_body,
            headers={
                "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE
            },
        )

    @patch("requests.post")
    def test_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "status": PaymentStatuses.FAIL.value,
            "errors": ["wrong number"],
        }
        order_id = 2
        card_number = "87654321"
        payment = Decimal("50.00")

        third_party_payment_service(
            url="http://example.com/api/payment/webhook/",
            order_id=order_id,
            card_number=card_number,
            payment=payment,
        )
        expected_body = {
            "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE,
            "order_id": order_id,
            "status": PaymentStatuses.FAIL.value,
            "errors": ["wrong number"],
            "payment_id": f"{order_id}test_payment_id",
        }
        fake_url = "http://app:8000/api/payment/webhook/"
        mock_post.assert_called_once_with(
            fake_url,
            json=expected_body,
            headers={
                "PAYMENT_SERVICE_SIGNATURE": settings.PAYMENT_SERVICE_SIGNATURE
            },
        )
