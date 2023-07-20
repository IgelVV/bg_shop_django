from unittest.mock import patch, ANY, MagicMock, call, PropertyMock

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from orders import models, services, selectors

UserModel = get_user_model()


class OrderServiceCreateOrderTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.OrderService()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="test_user",
            password="password",
        )
        self.order = models.Order.objects.create(
            user=self.user
        )
        self.created_at = timezone.now()

    def test_create_order_with_only_user(self):
        new_order = self.service.create_order(user=self.user)
        saved_order = models.Order.objects.get(pk=new_order.pk)
        self.assertEqual(new_order, saved_order)

    @patch.object(models.Order, 'full_clean')
    @patch.object(models.Order, 'save')
    @patch.object(services.OrderService, '_set_attributes')
    def test_set_attr(
            self, mock_set_attributes, mock_save, mock_full_clean):
        mock_set_attributes.return_value = self.order
        order_attrs = {
            'user': self.user,
            'created_at': self.created_at,
            'delivery_type': models.Order.DeliveryTypes.EXPRESS,
            'status': models.Order.Statuses.ACCEPTED,
            'city': 'New York',
            'address': '123 Main St',
            'comment': 'This is a test order',
            'paid': True,
            'payment_type': models.Order.PaymentTypes.CASH,
            'is_active': True,
        }
        new_order = self.service.create_order(**order_attrs)

        mock_set_attributes.assert_called_once_with(
            ANY,
            **order_attrs,
        )
        mock_save.assert_called_once()
        mock_full_clean.assert_called_once()
        self.assertEqual(new_order, self.order)

    @patch.object(models.Order, 'full_clean')
    @patch.object(models.Order, 'save')
    @patch.object(services.OrderService, '_set_attributes')
    def test_create_order_no_commit(
            self, mock_set_attributes, mock_save, mock_full_clean):
        mock_set_attributes.return_value = self.order
        order_attrs = {
            'user': self.user,
            'created_at': self.created_at,
            'delivery_type': models.Order.DeliveryTypes.EXPRESS,
            'status': models.Order.Statuses.ACCEPTED,
            'city': 'New York',
            'address': '123 Main St',
            'comment': 'This is a test order',
            'paid': True,
            'payment_type': models.Order.PaymentTypes.CASH,
            'is_active': True,
        }
        new_order = self.service.create_order(commit=False, **order_attrs)
        mock_set_attributes.assert_called_once_with(
            ANY,
            **order_attrs,
        )

        mock_save.assert_not_called()
        mock_full_clean.assert_not_called()
        self.assertEqual(new_order, self.order)


class OrderServiceSetAttributesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = services.OrderService()

        cls.created_at = timezone.now()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="test_user",
            password="password",
        )
        self.order = models.Order.objects.create(
            user=self.user
        )

    def test_set_attributes(self):
        attrs = {
            'user': self.user,
            'created_at': self.created_at,
            'delivery_type': models.Order.DeliveryTypes.EXPRESS,
            'status': models.Order.Statuses.ACCEPTED,
            'city': 'New York',
            'address': '123 Main St',
            'comment': 'This is a test order',
            'paid': True,
            'payment_type': models.Order.PaymentTypes.CASH,
            'is_active': True,
        }

        updated_order = self.service._set_attributes(self.order, **attrs)

        self.assertEqual(updated_order.user, self.user)
        self.assertEqual(updated_order.created_at, self.created_at)
        self.assertEqual(
            updated_order.delivery_type, models.Order.DeliveryTypes.EXPRESS)
        self.assertEqual(updated_order.status, models.Order.Statuses.ACCEPTED)
        self.assertEqual(updated_order.city, 'New York')
        self.assertEqual(updated_order.address, '123 Main St')
        self.assertEqual(updated_order.comment, 'This is a test order')
        self.assertTrue(updated_order.paid)
        self.assertEqual(
            updated_order.payment_type, models.Order.PaymentTypes.CASH)
        self.assertTrue(updated_order.is_active)

    def test_set_invalid_attribute(self):
        attrs = {
            'invalid_attribute': 'Invalid Value',
        }
        with self.assertRaises(AttributeError):
            self.service._set_attributes(self.order, **attrs)


class OrderServiceEditTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_service = services.OrderService()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            username="test_user",
            password="password",
        )

    @patch('orders.services.OrderService.update_ordered_products')
    @patch('orders.services.OrderService._set_attributes')
    def test_set_attrs_and_updates_products(
            self, mock_set_attributes, mock_update_ordered_products):
        order = models.Order(
            user=self.user,
            delivery_type=models.Order.DeliveryTypes.ORDINARY,
            status=models.Order.Statuses.ACCEPTED,
            city='New York',
            address='123 Main St',
            comment='This is a test order',
        )
        mock_set_attributes.return_value = order
        order_attrs = {
            'delivery_type': models.Order.DeliveryTypes.EXPRESS,
            'city': 'Moscow',
            'address': 'Red Square 1',
            'comment': '',
        }
        products = [
            {'id': 1, 'count': 2},
            {'id': 2, 'count': 1},
        ]
        edited_order = self.order_service.edit(
            order=order,
            order_attrs=order_attrs,
            products=products,
        )

        self.assertEqual(edited_order.status, models.Order.Statuses.EDITING)

        saved_order = models.Order.objects.get(pk=edited_order.pk)
        self.assertEqual(edited_order, saved_order)
        mock_set_attributes.assert_called_once_with(order=order, **order_attrs)
        mock_update_ordered_products.assert_called_once_with(
            order=order, products=products)

    @patch.object(models.Order, 'full_clean')
    @patch.object(models.Order, 'save')
    def test_no_commit(self, mock_save, mock_full_clean):
        order = models.Order(
            user=self.user,
        )
        edited_order = self.order_service.edit(
            order=order,
            commit=False,
        )

        mock_save.assert_not_called()
        mock_full_clean.assert_not_called()
        self.assertEqual(edited_order, order)


class OrderServiceUpdateOrderedProductsTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_service = services.OrderService()

    def setUp(self) -> None:
        self.order = models.Order.objects.get(
            pk=1
        )

    @patch.object(services.OrderService, '_simplify_products')
    @patch.object(services.OrderedProductService, 'create_ordered_product')
    @patch.object(services.OrderedProductService, 'update_price')
    def test_update_ordered_products(
            self,
            mock_update_price,
            mock_create_ordered_product,
            mock_simplify_products,
    ):
        mock_simplify_products.return_value = {
            1: 4,
            2: 5,
            3: 2,
        }
        products = [
            {'id': 1, 'count': 4},
            {'id': 2, 'count': 5},
            {'id': 3, 'count': 2},
        ]
        self.order_service.update_ordered_products(
            order=self.order, products=products)
        ordered_product_1 = models.OrderedProduct.objects.get(pk=1)
        ordered_product_2 = models.OrderedProduct.objects.get(pk=2)

        self.assertEqual(ordered_product_1.count, 4)
        self.assertEqual(ordered_product_2.count, 5)
        mock_simplify_products.assert_called_once_with(products=products)

        expected_update_calls = [
            call(ordered_product_1, commit=False),
            call(ordered_product_2, commit=False),
        ]
        mock_update_price.assert_has_calls(
            expected_update_calls, any_order=True)
        mock_create_ordered_product.assert_called_once_with(
            order=self.order, product_id=3, quantity=2,)


class OrderServiceSimplifyProductsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_service = services.OrderService()

    def test_simplify_products(self):
        products = [
            {'id': 1, 'count': 3},
            {'id': 2, 'count': 5},
            {'id': 3, 'count': 2},
        ]
        simplified_products = self.order_service._simplify_products(products)
        expected_simplified_products = {
            1: 3,
            2: 5,
            3: 2,
        }
        self.assertEqual(simplified_products, expected_simplified_products)

    def test_simplify_products_empty_list(self):
        products = []
        simplified_products = self.order_service._simplify_products(products)

        self.assertEqual(simplified_products, {})

    def test_simplify_products_duplicate_ids(self):
        products = [
            {'id': 1, 'count': 3},
            {'id': 1, 'count': 5},
        ]

        simplified_products = self.order_service._simplify_products(products)
        expected_simplified_products = {
            1: 5,
        }
        self.assertEqual(simplified_products, expected_simplified_products)

    def test_simplify_products_missing_count(self):
        products = [
            {'id': 1},
            {'id': 2, 'count': 5},
        ]
        with self.assertRaises(KeyError):
            self.order_service._simplify_products(products)


class OrderServiceConfirmTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    class DummyOrderedProductQuerySet:
        def __init__(self, order):
            self.qs = order.orderedproduct_set.all()

        def __eq__(self, other):
            return list(other.values()) == list(self.qs.values())

        def __ne__(self, other):
            return list(other.values()) != list(self.qs.values())

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_service = services.OrderService()

    def setUp(self) -> None:
        self.order_id = 1
        self.user = UserModel.objects.get(pk=1)
        self.order_data = {
            "delivery_type": models.Order.DeliveryTypes.EXPRESS,
            "city": "New York",
            "address": "123 Main St",
            "comment": "This is a test order",
        }

    @patch.object(services.OrderedProductService, "update_price")
    @patch.object(services.OrderedProductService, "deduct_amount_from_product")
    @patch.object(services.OrderService, "edit", )
    @patch.object(services.OrderService, "_parse_order_data")
    @patch.object(selectors.OrderSelector, "get_editing_order_of_user")
    def test_confirm_order(
            self,
            mock_get_editing_order_of_user,
            mock_parse_order_data,
            mock_edit,
            mock_deduct,
            mock_update_price
    ):

        order = models.Order.objects.get(pk=self.order_id)

        mock_get_editing_order_of_user.return_value = order
        mock_parse_order_data.return_value = self.order_data
        mock_edit.return_value = order

        self.order_service.confirm(
            order_id=self.order_id, user=self.user, order_data=self.order_data)

        mock_deduct.assert_called_once_with(
            ord_prod_qs=self.DummyOrderedProductQuerySet(order))
        self.assertEqual(
            mock_update_price.call_count, len(order.orderedproduct_set.all()))

        order.refresh_from_db()
        self.assertEqual(order.status, models.Order.Statuses.ACCEPTED)

    # def test_confirm_order_not_found(self):
    #     # Mock the OrderSelector's get_editing_order_of_user method to return None
    #     with patch.object(selectors.OrderSelector, "get_editing_order_of_user", return_value=None):
    #         with self.assertRaises(models.Order.DoesNotExist):
    #             # Call the confirm function with a non-existing order
    #             self.order_service.confirm(order_id=self.order_id, user=self.user, order_data=self.order_data)
