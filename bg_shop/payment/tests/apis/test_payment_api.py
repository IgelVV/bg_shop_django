from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from orders import models as order_models

UserModel = get_user_model()


class ComparableUrl:
    def __init__(self, url: str):
        self.url = url

    def __eq__(self, other: str):
        return other.endswith(self.url)

    def __ne__(self, other: str):
        return not other.endswith(self.url)


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

    def test_start_payment_with_invalid_data(self):
        data = {"number": "invalid_card_number"}
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("payment.tasks.third_party_payment_service")
    def test_start_payment_with_invalid_order_id(self, mock_payment):
        url = reverse("api:payment:payment", kwargs={'id': 9999})
        data = {"number": "12345678"}
        response = self.client.post(url, data=data,)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_payment.delay.assert_not_called()

    @patch("payment.tasks.third_party_payment_service")
    def test_order_of_other_user(self, mock_payment):
        other_user = UserModel.objects.create_user(
            username="other_test_user",
            password="",
        )
        other_order = order_models.Order.objects.create(
            user=other_user
        )
        url = reverse("api:payment:payment", kwargs={'id': other_order.pk})
        data = {"number": "12345678"}
        response = self.client.post(url, data=data,)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_payment.delay.assert_not_called()
