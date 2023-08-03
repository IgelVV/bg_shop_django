from unittest import mock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

from rest_framework import request as drf_request

from django.contrib.auth import get_user_model

from orders import models, services
from shop import models as shop_models

UserModel = get_user_model()


def create_session(request: drf_request):
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()


class SaveSessionTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        create_session(self.request)
        self.service = services.CartService(self.request)

    def test_cart_service_save_session(self):
        self.request.session.modified = False
        self.service.save_session()

        self.assertTrue(self.request.session.modified)


class CartServiceTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
    ]

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserModel.objects.get(pk=1)
        self.request.user = self.user
        create_session(self.request)
        self.product = shop_models.Product.objects.get(pk=1)

    def test_add_if_user_is_anonymous(self):
        self.request.user = AnonymousUser()
        service = services.CartService(request=self.request)
        service.add(product_id=self.product.id, quantity=2)

        cart = self.request.session[settings.CART_SESSION_ID]
        self.assertEqual(
            cart,
            {str(self.product.id): 2},
            "Unexpected session cart data."
        )

    def test_add_if_user_is_authenticated(self):
        order = models.Order.objects.create(
            user=self.request.user,
            status=models.Order.Statuses.CART,
        )
        service = services.CartService(request=self.request)
        service.add(product_id=self.product.id, quantity=3)
        order.refresh_from_db()
        self.assertEqual(
            order.orderedproduct_set.first().count,
            3,
            "Unexpected amount."
        )
        self.assertEqual(
            order.orderedproduct_set.first().product_id,
            self.product.id,
            "Unexpected product id."
        )

    def test_add_override_quantity(self):
        service = services.CartService(request=self.request)
        service.add(product_id=self.product.id, quantity=2)

        service.add(
            product_id=self.product.id, quantity=3, override_quantity=True)
        ordered_product = models.OrderedProduct.objects.get(
            product_id=self.product.id,
            order__user=self.user,
        )
        self.assertEqual(
            ordered_product.count,
            3,
            "Unexpected amount."
        )

    def test_add_unavailable_product(self):
        inactive_product = shop_models.Product.objects.get(pk=4)
        service = services.CartService(request=self.request)
        with self.assertRaises(
                ValueError,
                msg="Unavailable Product must rise Exception."
        ):
            service.add(product_id=inactive_product.id, quantity=3)


class AddToSessionTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        create_session(self.request)
        self.cart_service = services.CartService(self.request)

    def test_add_to_session(self):
        product_id = 1
        quantity = 2
        self.cart_service._add_to_session(
            product_id=product_id, quantity=quantity)

        cart = self.request.session[settings.CART_SESSION_ID]
        self.assertEqual(
            cart,
            {str(product_id): 2},
            "Unexpected session cart data."
        )

    def test_add_to_session_override_quantity(self):
        product_id = 1
        self.cart_service._add_to_session(product_id=product_id, quantity=2)
        self.cart_service._add_to_session(
            product_id=product_id, quantity=3, override_quantity=True)

        cart = self.request.session[settings.CART_SESSION_ID]
        self.assertEqual(
            cart,
            {str(product_id): 3},
            "Unexpected session cart data."
        )

    def test_add_to_session_not_override_quantity(self):
        product_id = 1
        self.cart_service._add_to_session(product_id=product_id, quantity=2)
        self.cart_service._add_to_session(product_id=product_id, quantity=3)

        cart = self.request.session[settings.CART_SESSION_ID]
        self.assertEqual(
            cart,
            {str(product_id): 5},
            "Unexpected session cart data."
        )


class AddToOrderTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        create_session(self.request)
        self.request.user = UserModel.objects.create_user(
            username='testuser', password='testpassword')
        self.product = shop_models.Product.objects.get(pk=1)
        self.cart_service = services.CartService(self.request)

    def test_add_to_order(self):
        self.cart_service._add_to_order(product_id=self.product.id,
                                        quantity=3)
        order = self.request.user.order_set.first()
        self.assertEqual(
            order.orderedproduct_set.first().count,
            3,
            "Unexpected amount."
        )
        self.assertEqual(
            order.orderedproduct_set.first().product_id,
            self.product.id,
            "Unexpected product id."
        )

    def test_add_to_order_override_quantity(self):
        self.cart_service._add_to_order(
            product_id=self.product.id, quantity=2)
        self.cart_service._add_to_order(
            product_id=self.product.id, quantity=3, override_quantity=True, )
        order = self.request.user.order_set.first()
        self.assertEqual(
            order.orderedproduct_set.first().count,
            3,
            "Unexpected amount."
        )
        self.assertEqual(
            order.orderedproduct_set.first().product_id,
            self.product.id,
            "Unexpected product id."
        )

    def test_add_to_order_not_override_quantity(self):
        self.cart_service._add_to_order(
            product_id=self.product.id, quantity=2)
        self.cart_service._add_to_order(
            product_id=self.product.id, quantity=3)
        order = self.request.user.order_set.first()
        self.assertEqual(
            order.orderedproduct_set.first().count,
            5,
            "Unexpected amount."
        )
        self.assertEqual(
            order.orderedproduct_set.first().product_id,
            self.product.id,
            "Unexpected product id."
        )


class RemoveTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        create_session(self.request)
        self.request.user = UserModel.objects.create_user(
            username='testuser', password='testpassword')
        self.cart_service = services.CartService(self.request)

    @mock.patch(
        "orders.services.CartService._remove_from_session", return_value=None)
    def test_remove_if_anonymous(self, mock_remove_from_session):
        self.request.user = AnonymousUser()
        product_id = 1
        quantity = 2
        self.cart_service.remove(product_id, quantity)
        mock_remove_from_session.assert_called_once_with(
            product_id, quantity)

    @mock.patch(
        "orders.services.CartService._remove_from_order", return_value=None)
    def test_remove_if_authenticated(self, mock_remove_from_order):
        product_id = 1
        quantity = 2
        self.cart_service.remove(product_id, quantity)
        mock_remove_from_order.assert_called_once_with(
            product_id, quantity)


class RemoveFromSessionTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        create_session(self.request)
        self.cart_service = services.CartService(self.request)

    def test_remove_part_of_products(self):
        product_id = 1
        self.request.session[settings.CART_SESSION_ID] = {str(product_id): 5}
        self.request.session.modified = True

        cart_service = services.CartService(self.request)
        quantity = 2
        cart_service._remove_from_session(
            product_id=product_id, quantity=quantity)

        cart = self.request.session[settings.CART_SESSION_ID]
        self.assertEqual(cart, {str(product_id): 3})

    def test_product_not_in_cart(self):
        product_id = 1
        quantity = 2

        self.cart_service._remove_from_session(
            product_id=product_id, quantity=quantity)

        cart = self.request.session.get(settings.CART_SESSION_ID, {})
        self.assertEqual(cart, {}, "Cart must be empty.")

    def test_remove_more_than_there_is(self):
        product_id = 1
        self.request.session[settings.CART_SESSION_ID] = {str(product_id): 1}
        self.request.session.modified = True
        cart_service = services.CartService(self.request)
        quantity = 2
        cart_service._remove_from_session(
            product_id=product_id, quantity=quantity)

        cart = self.request.session.get(settings.CART_SESSION_ID, {})
        self.assertEqual(cart, {}, "Cart must be empty.")

    @mock.patch('orders.services.CartService.save_session')
    def test_remove_from_session_save_session_called(self, mock_save_session):
        product_id = 1
        self.request.session[settings.CART_SESSION_ID] = {str(product_id): 5}
        self.request.session.modified = True
        cart_service = services.CartService(self.request)
        quantity = 2
        cart_service._remove_from_session(
            product_id=product_id, quantity=quantity)

        mock_save_session.assert_called_once()


class RemoveFromOrderTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = UserModel.objects.create_user(
            username='testuser', password='testpassword')
        create_session(self.request)
        self.cart_service = services.CartService(request=self.request)

    def test_remove_part_of_products(self):
        product_id = 1
        order = models.Order.objects.create(
            user=self.request.user,
            status=models.Order.Statuses.CART,
        )
        ordered_product = models.OrderedProduct.objects.create(
            order=order,
            product_id=product_id,
            count=5,
        )
        quantity = 3
        self.cart_service._remove_from_order(
            product_id=product_id, quantity=quantity)

        ordered_product.refresh_from_db()
        self.assertEqual(ordered_product.count, 2)

    def test_product_not_in_cart(self):
        product_id = 1
        order = models.Order.objects.create(
            user=self.request.user,
            status=models.Order.Statuses.CART,
        )
        quantity = 3
        self.cart_service._remove_from_order(
            product_id=product_id, quantity=quantity)

        self.assertFalse(order.orderedproduct_set.all())

    def test_quantity_greater_than_in_cart(self):
        product_id = 1
        order = models.Order.objects.create(
            user=self.request.user,
            status=models.Order.Statuses.CART,
        )
        ordered_product = models.OrderedProduct.objects.create(
            order=order,
            product_id=product_id,
            count=2,
        )
        quantity = 3
        self.cart_service._remove_from_order(
            product_id=product_id, quantity=quantity)

        with self.assertRaises(
                models.OrderedProduct.DoesNotExist,
                msg="OrderedProduct must be removed.",
        ):
            ordered_product.refresh_from_db()


class MergeCartsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        create_session(self.request)
        self.request.user = UserModel.objects.create_user(
            username='testuser', password='testpassword')
        self.cart_service = services.CartService(self.request)

    @mock.patch('orders.services.CartService._add_to_order', return_value=None)
    def test_merge_carts(self, mock_add_to_order):
        session_cart = {'1': 2, '2': 3}
        self.cart_service.merge_carts(session_cart)
        mock_add_to_order.assert_has_calls([
            mock.call(product_id=1, quantity=2, override_quantity=True),
            mock.call(product_id=2, quantity=3, override_quantity=True)
        ])

    @mock.patch('orders.services.CartService._add_to_order')
    def test_merge_carts_empty_session_cart(self, mock_add_to_order):
        session_cart = {}
        mock_add_to_order.return_value = None

        self.cart_service.merge_carts(session_cart)

        mock_add_to_order.assert_not_called()
