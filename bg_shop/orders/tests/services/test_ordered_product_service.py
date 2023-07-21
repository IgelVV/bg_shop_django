from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from orders import services, models, selectors
from shop import models as shop_models


class CreateOrderedProductTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
    ]

    def setUp(self):
        self.order = models.Order.objects.create(user_id=1)
        self.product_id = 1
        self.quantity = 3
        self.service = services.OrderedProductService()

    @patch.object(services.OrderedProductService, 'refresh_price_from_product')
    def test_create_ordered_product_with_commit_true(self, mock_refresh_price):
        ordered_product_count_before = models.OrderedProduct.objects.count()

        ordered_product = self.service.create_ordered_product(
            order=self.order,
            product_id=self.product_id,
            quantity=self.quantity,
            commit=True,
        )

        ordered_product_count_after = models.OrderedProduct.objects.count()
        self.assertEqual(
            ordered_product_count_after, ordered_product_count_before + 1)
        self.assertEqual(ordered_product.order, self.order)
        self.assertEqual(ordered_product.product_id, self.product_id)
        self.assertEqual(ordered_product.count, self.quantity)
        mock_refresh_price.assert_called_once_with(
            ordered_product=ordered_product, commit=False)

    @patch.object(services.OrderedProductService, 'refresh_price_from_product')
    def test_create_ordered_product_with_commit_false(self, mock_refresh_price):
        ordered_product_count_before = models.OrderedProduct.objects.count()

        ordered_product = self.service.create_ordered_product(
            order=self.order,
            product_id=self.product_id,
            quantity=self.quantity,
            commit=False,
        )

        ordered_product_count_after = models.OrderedProduct.objects.count()
        self.assertEqual(
            ordered_product_count_after, ordered_product_count_before)
        with self.assertRaises(models.OrderedProduct.DoesNotExist):
            models.OrderedProduct.objects.get(
                order=self.order, product_id=self.product_id)
        self.assertEqual(ordered_product.order, self.order)
        self.assertEqual(ordered_product.product_id, self.product_id)
        self.assertEqual(ordered_product.count, self.quantity)
        mock_refresh_price.assert_called_once_with(
            ordered_product=ordered_product, commit=False)

    @patch.object(services.OrderedProductService, 'refresh_price_from_product')
    def test_create_ordered_product_with_wrong_params(
            self, mock_refresh_price):
        ordered_product_count_before = models.OrderedProduct.objects.count()
        with self.assertRaises(ValidationError):
            self.service.create_ordered_product(
                order=self.order,
                product_id=self.product_id,
                quantity=(-1),
                commit=True,
            )
        ordered_product_count_after = models.OrderedProduct.objects.count()
        self.assertEqual(
            ordered_product_count_after, ordered_product_count_before)


class AddItemTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
    ]

    def setUp(self):
        self.order = models.Order.objects.get(pk=1)
        self.product_id = 1
        self.service = services.OrderedProductService()

    @patch.object(services.OrderedProductService, 'reduce_or_delete')
    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_add_item_override_quantity_true(
            self, mock_get_ordered_product,
            mock_reduce_or_delete,
    ):
        mock_get_ordered_product.return_value = models.OrderedProduct(
            order=self.order, product_id=self.product_id, count=2
        )
        quantity = 3
        self.service.add_item(
            order=self.order,
            product_id=self.product_id,
            quantity=quantity,
            override_quantity=True,
        )
        ordered_product = models.OrderedProduct.objects.get(
            order=self.order, product_id=self.product_id)
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)
        self.assertEqual(ordered_product.count, quantity)
        mock_reduce_or_delete.assert_not_called()

    @patch.object(services.OrderedProductService, 'reduce_or_delete')
    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_add_item_override_quantity_false(
            self,
            mock_get_ordered_product,
            mock_reduce_or_delete
    ):
        mock_get_ordered_product.return_value = models.OrderedProduct(
            order=self.order, product_id=self.product_id, count=2
        )
        quantity = 3
        self.service.add_item(
            order=self.order,
            product_id=self.product_id,
            quantity=quantity,
            override_quantity=False,
        )
        ordered_product = models.OrderedProduct.objects.get(
            order=self.order, product_id=self.product_id)
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)
        self.assertEqual(ordered_product.count, 5)
        mock_reduce_or_delete.assert_not_called()

    @patch.object(services.OrderedProductService, 'reduce_or_delete')
    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_add_item_with_negative_quantity(
            self,
            mock_get_ordered_product,
            mock_reduce_or_delete
    ):
        mock_get_ordered_product.return_value = models.OrderedProduct(
            order=self.order, product_id=self.product_id, count=5
        )

        self.service.add_item(
            order=self.order,
            product_id=self.product_id,
            quantity=-4,
            override_quantity=True,
        )

        mock_reduce_or_delete.assert_called_once_with(
            order=self.order, product_id=self.product_id, quantity=4
        )
        mock_get_ordered_product.assert_not_called()

    @patch.object(services.OrderedProductService, 'reduce_or_delete')
    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_add_item_without_existing_ordered_product(
            self,
            mock_get_ordered_product,
            mock_reduce_or_delete
    ):
        mock_get_ordered_product.return_value = None
        quantity = 3
        self.service.add_item(
            order=self.order,
            product_id=self.product_id,
            quantity=quantity,
            override_quantity=False,
        )
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)
        ordered_product = models.OrderedProduct.objects.get(
            order=self.order, product_id=self.product_id)
        self.assertEqual(ordered_product.count, quantity)
        mock_reduce_or_delete.assert_not_called()


class ReduceOrDeleteTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
    ]

    def setUp(self):
        self.order = models.Order.objects.get(pk=1)
        self.product_id = 1
        self.quantity = 2
        self.service = services.OrderedProductService()

    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_reduce_or_delete_quantity_less_than_ordered_product_count(
            self, mock_get_ordered_product):
        ordered_product = models.OrderedProduct.objects.create(
            order=self.order, product_id=self.product_id, count=3,
        )
        mock_get_ordered_product.return_value = ordered_product
        ordered_product_count_before = ordered_product.count

        self.service.reduce_or_delete(
            order=self.order,
            product_id=self.product_id,
            quantity=self.quantity,
        )

        ordered_product.refresh_from_db()
        self.assertEqual(
            ordered_product.count, ordered_product_count_before - self.quantity
        )
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)

    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_reduce_or_delete_quantity_greater_than_ordered_product_count(
            self, mock_get_ordered_product):
        ordered_product = models.OrderedProduct.objects.create(
            order=self.order, product_id=self.product_id, count=self.quantity,
        )
        mock_get_ordered_product.return_value = ordered_product

        self.service.reduce_or_delete(
            order=self.order,
            product_id=self.product_id,
            quantity=self.quantity + 1,
        )

        with self.assertRaises(models.OrderedProduct.DoesNotExist):
            models.OrderedProduct.objects.get(
                order=self.order, product_id=self.product_id
            )
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)

    @patch.object(
        selectors.OrderedProductSelector, 'get_ordered_product_from_order')
    def test_reduce_or_delete_non_existing_ordered_product(
            self, mock_get_ordered_product):
        mock_get_ordered_product.return_value = None
        with self.assertRaises(models.OrderedProduct.DoesNotExist):
            self.service.reduce_or_delete(
                order=self.order,
                product_id=self.product_id,
                quantity=self.quantity,
            )
        mock_get_ordered_product.assert_called_once_with(
            order=self.order, product_id=self.product_id)


class RefreshPriceFromProductTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self):
        self.ordered_product = models.OrderedProduct.objects.get(pk=1)
        self.service = services.OrderedProductService()

    @patch('shop.selectors.ProductSelector.get_discounted_price')
    def test_refresh_price_from_product_with_commit_true(
            self, mock_get_discounted_price):
        mock_get_discounted_price.return_value = Decimal(20)

        self.service.refresh_price_from_product(
            ordered_product=self.ordered_product,
            commit=True,
        )
        self.ordered_product.refresh_from_db()
        self.assertEqual(self.ordered_product.price, 20.0)

    @patch('shop.selectors.ProductSelector.get_discounted_price')
    def test_refresh_price_from_product_with_commit_false(
            self, mock_get_discounted_price):
        mock_get_discounted_price.return_value = Decimal(20)
        price_before = self.ordered_product.price

        self.service.refresh_price_from_product(
            ordered_product=self.ordered_product,
            commit=False,
        )

        self.ordered_product.refresh_from_db()
        self.assertEqual(self.ordered_product.price, price_before)


class DeductAmountFromProductTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self):
        self.ordered_products = models.OrderedProduct.objects.filter(
            pk__in=[1, 2]).order_by("pk")
        self.product_1 = shop_models.Product.objects.get(pk=1)
        self.product_2 = shop_models.Product.objects.get(pk=2)
        self.service = services.OrderedProductService()

    def test_deduct_from_product_with_valid_count_and_active_product(self):
        initial_count_1 = self.product_1.count
        initial_count_2 = self.product_2.count

        self.service.deduct_amount_from_product(
            ord_prod_qs=self.ordered_products)

        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(
            self.product_1.count,
            initial_count_1 - self.ordered_products[0].count,
        )
        self.assertEqual(
            self.product_2.count,
            initial_count_2 - self.ordered_products[1].count,
        )

    def test_deduct_amount_from_product_with_insufficient_product_count(self):
        self.product_2.count = 1
        self.product_2.save()
        self.product_2.refresh_from_db()

        initial_count_1 = self.product_1.count
        initial_count_2 = self.product_2.count

        with self.assertRaises(ValueError):
            self.service.deduct_amount_from_product(
                ord_prod_qs=self.ordered_products)

        # check transaction roll back
        self.assertEqual(
            self.product_1.count,
            initial_count_1,
        )
        self.assertEqual(
            self.product_2.count,
            initial_count_2,
        )

    def test_deduct_amount_from_product_with_inactive_product(self):
        self.product_2.is_active = False
        self.product_2.save()
        self.product_2.refresh_from_db()

        initial_count_1 = self.product_1.count
        initial_count_2 = self.product_2.count

        with self.assertRaises(ValueError):
            self.service.deduct_amount_from_product(
                ord_prod_qs=self.ordered_products)

        # check transaction roll back
        self.assertEqual(
            self.product_1.count,
            initial_count_1,
        )
        self.assertEqual(
            self.product_2.count,
            initial_count_2,
        )


class ReturnOrderedProductsTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_order",
        "test_ordered_product",
    ]

    def setUp(self):
        self.ordered_products = models.OrderedProduct.objects.filter(
            pk__in=[1, 2]).order_by("pk")
        self.product_1 = shop_models.Product.objects.get(pk=1)
        self.product_2 = shop_models.Product.objects.get(pk=2)
        self.service = services.OrderedProductService()

    def test_return_ordered_products(self):
        initial_count_1 = self.product_1.count
        initial_count_2 = self.product_2.count

        self.service.return_ordered_products(ord_prod_qs=self.ordered_products)

        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(
            self.product_1.count,
            initial_count_1 + self.ordered_products[0].count,
        )
        self.assertEqual(
            self.product_2.count,
            initial_count_2 + self.ordered_products[1].count,
        )

    @patch.object(shop_models.Product, "save")
    def test_return_nonexistent_ordered_product(self, mock_product_save):
        self.service.return_ordered_products(
            ord_prod_qs=models.OrderedProduct.objects.filter(pk=999))
        mock_product_save.assert_not_called()


