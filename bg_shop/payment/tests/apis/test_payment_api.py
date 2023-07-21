from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, override_settings, APIRequestFactory

UserModel = get_user_model()


class ComparableUrl:
    def __init__(self, url: str):
        self.url = url

    def __eq__(self, other: str):
        return other.endswith(self.url)

    def __ne__(self, other: str):
        return not other.endswith(self.url)


# @override_settings(DEBUG=True)
class PaymentApiTestCase(APITestCase):
    url = reverse("api:payment:payment", kwargs={'id': 1})
    fixtures = [
        "test_user",
        "test_order",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.client.force_login(self.user)

    @patch("payment.tasks.third_party_payment_service", )
    def test_start_payment_with_valid_data(self, mock_payment):
        data = {"number": "12345678"}

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_payment.delay.assert_called_once_with(
            url=ComparableUrl(reverse("api:payment:payment-webhook")),
            order_id=1,
            card_number=data["number"],
            payment=1,
        )

    # def test_start_payment_with_invalid_data(self):
    #     order_id = 123  # Replace with a valid order ID
    #     data = {"number": "invalid_card_number"}  # Provide an invalid card number
    #     response = self.client.post(self.url, data=data, kwargs={"id": order_id})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     # Additional assertions based on the expected behavior for invalid input data.
    #
    # def test_start_payment_with_invalid_order_id(self):
    #     invalid_order_id = 999999  # Replace with a non-existing order ID
    #     data = {"number": "12345678"}  # Replace with a valid card number
    #     response = self.client.post(self.url, data=data, kwargs={"id": invalid_order_id})
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #
    #     # Additional assertions based on the expected behavior for invalid order ID.
