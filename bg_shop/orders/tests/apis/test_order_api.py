import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from orders import models

UserModel = get_user_model()


class GetOrderApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.url = reverse("api:orders:orders")

    def test_only_active_orders_in_response_without_cart_status(self):
        expected_orders_id = models.Order.objects \
            .exclude(status="CT") \
            .exclude(is_active=False).values_list("id", flat=True)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        simple_response_data = list(
            map(lambda order: order["id"], response.data))
        self.assertEqual(response.status_code, 200, "Wrong status code.")
        self.assertEqual(
            set(simple_response_data),
            set(expected_orders_id),
            "Wrong response data.",
        )

    def test_allow_only_for_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code. "
            "Perhaps the permission allows any user to get."
        )


class PostOrderApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.url = reverse("api:orders:orders")

    def test_creates_correct_order(self):
        # to prevent using Order with cart status.
        cart_order = models.Order.objects.get(pk=1)
        cart_order.status = "CO"
        cart_order.save()

        data = [
            {
                "id": 1,
                "category": 1,
                "price": 10,
                "count": 1,
                "date": "2023-06-10T15:53:01Z",
                "title": "test title",
                "description": "test description",
                "freeDelivery": True,
                "images": None,
                "tags": [],
                "reviews": 5,
                "rating": 10,
            }
        ]
        self.client.force_login(self.user)
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            200,
            "Wrong status code.",
        )

        created_order = models.Order.objects.get(pk=response.data['orderId'])
        self.assertEqual(
            created_order.status,
            models.Order.Statuses.EDITING,
            "Wrong status. Created order must have `ED` status."
        )

    def test_creates_correct_order_from_existing_cart_order(self):
        data = [
            {
                "id": 1,
                "category": 1,
                "price": 10,
                "count": 1,
                "date": "2023-06-10T15:53:01Z",
                "title": "test title",
                "description": "test description",
                "freeDelivery": True,
                "images": None,
                "tags": [],
                "reviews": 5,
                "rating": 10,
            }
        ]
        self.client.force_login(self.user)
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            200,
            "Wrong status code.",
        )

        expected_data = {'orderId': 1}
        self.assertEqual(
            expected_data,
            response.data,
            "Wrong response data. "
            "If order with status == `CT` exists, "
            "it must be used instead of creating new one."
        )
        created_order = models.Order.objects.get(pk=response.data['orderId'])
        self.assertEqual(
            created_order.status,
            models.Order.Statuses.EDITING,
            "Wrong status. Created order must have `ED` status."
        )

    def test_allow_only_for_authenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(
            response.status_code,
            403,
            "Wrong status code. "
            "Perhaps the permission allows any user to get."
        )
