from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model, login
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

from rest_framework import request as drf_request
from rest_framework.test import APIRequestFactory

from orders import models, apis

UserModel = get_user_model()


def add_product_to_session_cart(request: drf_request, product_id: str) -> None:
    if request.session.get(settings.CART_SESSION_ID, False):
        cart = request.session[settings.CART_SESSION_ID]
    else:
        cart = request.session[settings.CART_SESSION_ID] = {}
    if cart.get(product_id, False):
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session.modified = True


def create_session(request: drf_request):
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    return request


class GetCartApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.url = reverse("api:orders:basket")
        self.order_cart = models.Order.objects.get(pk=1)

    def test_anonymous_user_gets_session_cart(self):
        request = APIRequestFactory().get(self.url)
        request = create_session(request)
        add_product_to_session_cart(request=request, product_id="1")
        request.user = AnonymousUser()

        response = apis.CartApi.as_view()(request)
        self.assertEqual(response.status_code, 200, "Wrong status code")
        self.assertEqual(
            response.data[0].get("count"),
            1,
            "Wrong count (1 in session cart, 3 in order cart)",
        )

    def test_authenticated_user_gets_order_cart(self):
        request = APIRequestFactory().get(self.url)
        request = create_session(request)
        add_product_to_session_cart(request=request, product_id="1")
        request.user = None
        login(request=request, user=self.user)

        response = apis.CartApi.as_view()(request)
        self.assertEqual(response.status_code, 200, "Wrong status code")
        self.assertEqual(
            response.data[0].get("count"),
            3,
            "Wrong count (1 in session cart, 3 in order cart)",
        )

    def test_session_without_cart(self):
        request = APIRequestFactory().get(self.url)
        request = create_session(request)
        request.user = AnonymousUser()

        response = apis.CartApi.as_view()(request)
        self.assertEqual(response.status_code, 200, "Wrong status code")
        self.assertFalse(
            response.data,
            "Empty response is expected",
        )

    def test_user_does_not_have_order_cart_yet(self):
        self.user.order_set.all().delete()

        request = APIRequestFactory().get(self.url)
        request = create_session(request)
        request.user = None
        login(request=request, user=self.user)

        response = apis.CartApi.as_view()(request)
        self.assertEqual(response.status_code, 200, "Wrong status code")
        self.assertFalse(
            response.data,
            "Empty response is expected",
        )


class PostCartApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.url = reverse("api:orders:basket")
        self.order_cart = models.Order.objects.get(pk=1)

    def test_add_item_to_session_cart_if_user_is_anonymous(self):
        data = {
            "id": 1,
            "count": 2,
        }
        response = self.client.post(
            path=self.url,
            data=data,
        )
        self.assertEqual(response.status_code, 200, "Wrong status code.")

        self.assertEqual(response.data[0].get("id"), 1, "Wrong product id.")
        self.assertEqual(
            response.data[0].get("count"), 2, "Wrong product count.")

        # todo to service test
        # expected_session_cart = {
        #     "1": 2
        # }
        # self.assertEqual(
        #     expected_session_cart,
        #     self.client.session[settings.CART_SESSION_ID],
        #     "Wrong session cart",
        # )

    def test_add_item_to_order_cart_if_user_is_authenticated(self):
        data = {
            "id": 1,
            "count": 2,
        }
        self.client.force_login(self.user)
        response = self.client.post(
            path=self.url,
            data=data,
        )
        self.assertEqual(response.status_code, 200, "Wrong status code.")
        self.assertEqual(response.data[0].get("id"), 1, "Wrong product id.")
        self.assertEqual(
            response.data[0].get("count"),
            5,
            "Wrong product count, 5 is expected,"
            "because there are 3 items in the order cart before the request."
        )

        # todo to service test
        # self.assertEqual(
        #     self.order_cart.orderedproduct_set.all()[0].count,
        #     5,
        #     "Wrong OrderedProduct.count. "
        #     "Perhaps, item has not been added to cart."
        # )

    def test_invalid_data(self):
        data = {}
        response = self.client.post(
            path=self.url,
            data=data,
        )
        self.assertEqual(response.status_code, 400, "Wrong status code.")


class DeleteCartApiTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.url = reverse("api:orders:basket")
        self.order_cart = models.Order.objects.get(pk=1)

    def test_delete_if_anonymous(self):
        ...

    def test_delete_if_authenticated(self):
        ...

    def test_delete_from_empty_cart(self):
        ...
