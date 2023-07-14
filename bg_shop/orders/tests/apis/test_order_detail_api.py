import json

from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders import models

UserModel = get_user_model()


class GetOrderDetailApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.editing_order_id = 2
        self.url_order_cart = reverse(
            "api:orders:order_detail", kwargs={'id': 1})
        self.url_order_editing = reverse(
            "api:orders:order_detail", kwargs={'id': self.editing_order_id})
        self.url_non_existing_order = reverse(
            "api:orders:order_detail", kwargs={'id': 9999})

    def test_allow_only_for_authenticated(self):
        response = self.client.get(self.url_order_cart)
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code. "
            "Perhaps the permission allows any user to get."
        )

    def test_response_data_is_correct(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_order_editing)
        self.assertEqual(
            response.status_code,
            200,
            "Wrong status code. "
            "Perhaps the permission allows any user to get."
        )
        self.assertEqual(
            response.data['id'],
            self.editing_order_id,
            "Wrong response",
        )

    def test_get_cart_order(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_order_cart)
        self.assertEqual(
            response.status_code,
            404,
            "Api must not return orders with status == `CT` (cart)",
        )

    def test_get_non_existing_order(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_non_existing_order)
        self.assertEqual(
            response.status_code,
            404,
            "Wrong status code.",
        )


class PostOrderDetailApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.editing_order_id = 2
        self.url_order_editing = reverse(
            "api:orders:order_detail", kwargs={'id': self.editing_order_id})
        self.url_order_not_editing = reverse(
            "api:orders:order_detail", kwargs={'id': 1})

        data = {
            "id": 2,
            "createdAt": "2023-06-10T15:53:01Z",
            "fullName": None,
            "email": None,
            "phone": None,
            "deliveryType": "EX",
            "paymentType": "ON",
            "totalCost": None,
            "status": "ED",
            "city": "",
            "address": "",
            "comment": "",
            "is_active": True,
            "paid": False,
            "products": [],
        }

    @tag("celery")
    def test_confirm_order(self):
        data = {
            "id": 2,
            "createdAt": "2023-06-10T15:53:01Z",
            "deliveryType": "EX",
            "paymentType": "ON",
            "status": "ED",
            "address": "Baker st.221b",
            "comment": "",
            "city": "London",
            "products": [],
        }

        self.client.force_login(self.user)
        response = self.client.post(
            self.url_order_editing,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            200,
            "Wrong status code.",
        )
        order = models.Order.objects.get(pk=self.editing_order_id)
        self.assertEqual(
            order.status,
            models.Order.Statuses.ACCEPTED,
            "Order has not been confirmed.",
        )

    def test_confirm_not_editing_order(self):
        data = {
            "id": 2,
            "createdAt": "2023-06-10T15:53:01Z",
            "deliveryType": "EX",
            "paymentType": "ON",
            "status": "ED",
            "address": "Baker st.221b",
            "comment": "",
            "city": "London",
            "products": [],
        }

        self.client.force_login(self.user)
        response = self.client.post(
            self.url_order_not_editing,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            404,
            "Wrong status code.",
        )

    def test_allow_only_for_authenticated(self):
        response = self.client.post(self.url_order_editing)
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code. "
            "Perhaps the permission allows any user to get."
        )
