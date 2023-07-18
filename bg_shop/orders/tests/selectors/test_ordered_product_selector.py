from django.test import TestCase
from django.contrib.auth import get_user_model

from orders import models, selectors
from shop import models as shop_models

UserModel = get_user_model()


class GetOrderedProductFromOrderTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderedProductSelector()

    def setUp(self):
        self.user = UserModel.objects.get(pk=1)
        self.product = shop_models.Product.objects.get(pk=1)
        self.order = models.Order.objects.create(
            user=self.user,
        )
        self.ordered_product = models.OrderedProduct.objects.create(
            order=self.order,
            product=self.product,
            count=2,
            price=50,
        )

    def test_get_ordered_product_with_order(self):
        result = self.selector.get_ordered_product_from_order(
            order=self.order, product_id=self.product.pk)
        self.assertIsNotNone(result)
        self.assertEqual(
            result,
            self.ordered_product,
            "The result doesn't match the expected ordered product.",
        )

    def test_get_ordered_product_with_order_id(self):
        result = self.selector.get_ordered_product_from_order(
            order_id=self.order.pk, product_id=self.product.pk)
        self.assertIsNotNone(result)
        self.assertEqual(
            result,
            self.ordered_product,
            "The result doesn't match the expected ordered product.",
        )

    def test_get_ordered_product_with_invalid_args(self):
        with self.assertRaises(
                ValueError,
                msg="Only one of args ('oder' or 'order_id') can be passed.",
        ):
            self.selector.get_ordered_product_from_order(
                order=self.order,
                order_id=self.order.pk,
                product_id=self.product.pk,
            )

    def test_get_ordered_product_with_missing_args(self):
        with self.assertRaises(
                ValueError,
                msg="At least one of args ('oder' or 'order_id')"
                    " must be passed.",
        ):
            self.selector.get_ordered_product_from_order(
                product_id=self.product.pk)

    def test_get_ordered_product_with_nonexistent_product(self):
        result = self.selector.get_ordered_product_from_order(
            order=self.order, product_id=9999)
        self.assertIsNone(
            result, "If ordered product doesn't exist it must return None.")

    def test_get_ordered_product_with_nonexistent_order(self):
        result = self.selector.get_ordered_product_from_order(
            order_id=9999, product_id=self.product.pk)
        self.assertIsNone(
            result, "If ordered product doesn't exist it must return None.")
