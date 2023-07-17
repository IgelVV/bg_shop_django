from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import login
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

from rest_framework import request as drf_request
from rest_framework.test import APIRequestFactory

from django.contrib.auth import get_user_model

from orders import models, selectors
from shop import models as shop_models

UserModel = get_user_model()


def add_product_to_session_cart(
        request: drf_request,
        product_id: str,
        quantity: int = 1,
) -> None:
    if request.session.get(settings.CART_SESSION_ID, False):
        cart = request.session[settings.CART_SESSION_ID]
    else:
        cart = request.session[settings.CART_SESSION_ID] = {}
    if cart.get(product_id, False):
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    request.session.modified = True


def create_session(request: drf_request):
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    return request


class GetCartTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.order_cart = models.Order.objects.get(pk=1)

    def test_get_cart_if_user_is_anonymous(self):
        request = APIRequestFactory().get("/")
        request = create_session(request)
        add_product_to_session_cart(request=request, product_id="1")

        request.user = AnonymousUser()
        selector = selectors.CartSelector(request=request)

        result = selector.get_cart()
        self.assertEqual(
            set(result),
            {shop_models.Product.objects.get(pk=1), },
            "Unexpected result",
        )
        self.assertEqual(
            result[0].quantity_ordered,
            1,
            "Unexpected quantity of products added to the cart."
        )

        # check that it caches related objects and quantity ordered
        expected_cached_objects = {
            'tags', 'images', 'review_set', 'orderedproduct_set', 'sale_set'}
        self.assertEqual(
            expected_cached_objects,
            result[0]._prefetched_objects_cache.keys(),
            "Not all needed related objects has been prefetched."
        )
        self.assertTrue(
            hasattr(result[0], "quantity_ordered"),
            "`quantity_ordered` attribute hasn't been set."
        )

    def test_get_cart_if_user_is_authenticated(self):
        request = APIRequestFactory().get("/")
        request = create_session(request)
        request.user = None
        login(request=request, user=self.user)

        selector = selectors.CartSelector(request=request)
        result = selector.get_cart()

        self.assertEqual(
            set(shop_models.Product.objects.filter(pk__in=[1, 2])),
            set(result),
            "Unexpected result",
        )

        # check that it caches related objects and quantity ordered
        expected_cached_objects = {
            'tags', 'images', 'review_set', 'orderedproduct_set', 'sale_set'}
        self.assertEqual(
            expected_cached_objects,
            result[0]._prefetched_objects_cache.keys(),
            "Not all needed related objects has been prefetched."
        )
        self.assertTrue(
            hasattr(result[0], "quantity_ordered"),
            "`quantity_ordered` attribute hasn't been set."
        )

    def test_user_does_not_have_order_cart_yet(self):
        models.Order.objects.filter(user=self.user).delete()
        request = APIRequestFactory().get("/")
        request = create_session(request)
        request.user = None
        login(request=request, user=self.user)

        selector = selectors.CartSelector(request=request)
        result = selector.get_cart()

        self.assertEqual(
            [],
            result,
            "Unexpected result",
        )

    def test_session_without_cart(self):
        request = APIRequestFactory().get("/")
        request = create_session(request)

        request.user = AnonymousUser()
        selector = selectors.CartSelector(request=request)

        result = selector.get_cart()
        self.assertEqual(
            result,
            [],
            "Unexpected result",
        )
