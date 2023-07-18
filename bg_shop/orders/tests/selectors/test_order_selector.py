from decimal import Decimal

from django.http import Http404
from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model

from orders import models, selectors
from dynamic_config import services as d_conf_services

UserModel = get_user_model()


class GetOrdersTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()

    def test_get_all_orders(self):
        result = self.selector.get_orders()
        self.assertEqual(
            set(models.Order.objects.all()),
            set(result),
            "Not all orders received."
        )

    def test_filter_orders(self):
        result = self.selector.get_orders(
            filters={
                "user_id": 1,
                "status": models.Order.Statuses.EDITING,
                "is_active": True,
            }
        )
        expected_result = models.Order.objects.filter(
            user_id=1,
            status=models.Order.Statuses.EDITING,
            is_active=True,
        )
        self.assertEqual(
            set(expected_result),
            set(result),
            "Not all orders received."
        )


class GetOrCreateCartOrderTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()
        cls.user = UserModel.objects.get(pk=1)

    def test_get_existing_cart_order(self):
        expected_result = models.Order.objects.get(
            user=self.user,
            status=models.Order.Statuses.CART,
            is_active=True,
        )
        result = self.selector.get_or_create_cart_order(
            user=self.user,
            prefetch_ordered_products=False,
        )
        self.assertEqual(
            expected_result,
            result,
            "Existing Order with status=CART it not found.",
        )

    def test_create_cart_order_if_not_exists(self):
        models.Order.objects.filter(
            user=self.user,
            status=models.Order.Statuses.CART,
            is_active=True,
        ).delete()
        result = self.selector.get_or_create_cart_order(
            user=self.user,
            prefetch_ordered_products=False,
        )
        expected_result = models.Order.objects.get(
            user=self.user, status=models.Order.Statuses.CART)
        self.assertEqual(
            expected_result,
            result,
            "New order with CART status has not been created.",
        )

    def test_prefetch_ordered_products(self):
        result = self.selector.get_or_create_cart_order(
            user=self.user,
            prefetch_ordered_products=True,
        )
        expected_cached_objects = {'orderedproduct_set'}
        self.assertEqual(
            result._prefetched_objects_cache.keys(),
            expected_cached_objects,
            "Ordered products has not been prefetched."
        )


class GetCartOrderTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()
        cls.user = UserModel.objects.get(pk=1)

    def test_get_existing_cart_order(self):
        expected_result = models.Order.objects.get(
            user=self.user,
            status=models.Order.Statuses.CART,
            is_active=True,
        )
        result = self.selector.get_cart_order(
            user=self.user,
            prefetch_ordered_products=False,
        )
        self.assertEqual(
            expected_result,
            result,
            "Existing Order with status=CART it not found.",
        )

    def test_get_if_no_cart_orders(self):
        models.Order.objects.filter(
            user=self.user,
            status=models.Order.Statuses.CART,
        ).delete()
        result = self.selector.get_cart_order(
            user=self.user,
            prefetch_ordered_products=False,
        )
        expected_result = None
        self.assertEqual(
            expected_result,
            result,
            "New order with CART status has not been created.",
        )

    def test_prefetch_ordered_products(self):
        result = self.selector.get_cart_order(
            user=self.user,
            prefetch_ordered_products=True,
        )
        expected_cached_objects = {'orderedproduct_set'}
        self.assertEqual(
            result._prefetched_objects_cache.keys(),
            expected_cached_objects,
            "Ordered products has not been prefetched."
        )


class GetOrdersOfUserTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()
        cls.user = UserModel.objects.get(pk=1)

    def test_get_all_orders_of_user(self):
        expected_result = models.Order.objects.filter(
            user=self.user,
            is_active=True,
        )
        result = self.selector.get_orders_of_user(
            user=self.user,
            exclude_cart=False,
        )
        self.assertEqual(
            set(expected_result),
            set(result),
            "Unexpected result",
        )

    def test_exclude_cart(self):
        expected_result = models.Order.objects.filter(
            user=self.user,
            is_active=True,
        ).exclude(
            status=models.Order.Statuses.CART,
        )
        result = self.selector.get_orders_of_user(
            user=self.user,
            exclude_cart=True,
        )
        self.assertEqual(
            set(expected_result),
            set(result),
            "Unexpected result",
        )


class GetOrderHistoryTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()
        cls.user = UserModel.objects.get(pk=1)

    def test_get_all_active_orders_without_cart_with_cashed_data(self):
        expected_result = models.Order.objects.filter(
            user=self.user,
            is_active=True,
        ).exclude(
            status=models.Order.Statuses.CART,
        )
        result = self.selector.get_order_history(
            user=self.user,
            order_by_date=False,
        )
        self.assertEqual(
            set(expected_result),
            set(result),
            "Unexpected result",
        )

        self.assertEqual(
            result[0]._prefetched_objects_cache.keys(),
            {'orderedproduct_set'},
            "Ordered products has not been prefetched."
        )
        self.assertEqual(
            result[0]._state.fields_cache.keys(),
            {'user'},
            "Related User has not been selected."
        )
        self.assertIn(
            'product',
            result[0].orderedproduct_set.first()._state.fields_cache.keys(),
            "Related Product has not been selected."
        )
        product_cache = result[0].orderedproduct_set.first() \
            .product._prefetched_objects_cache.keys(),
        self.assertIn(
            {'sale_set', "images", "review_set"},
            product_cache,
            "objects related to the product has not been prefetched."
        )

    def test_order_by_date(self):
        expected_result = models.Order.objects.filter(
            user=self.user,
            is_active=True,
        ).exclude(
            status=models.Order.Statuses.CART,
        ).order_by('-created_at')

        result = self.selector.get_order_history(
            user=self.user,
            order_by_date=True,
        )
        self.assertEqual(
            list(expected_result),
            list(result),
            "Unexpected result",
        )


class PrefetchDataTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_profile",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()

    def test_main_data_prefetched(self):
        result = self.selector._prefetch_data(
            orders_qs=models.Order.objects.all(),
            with_images_and_reviews=False,
            with_user_profile=False,
        )
        self.assertEqual(
            result[0]._prefetched_objects_cache.keys(),
            {'orderedproduct_set'},
            "Ordered products has not been prefetched."
        )
        self.assertIn(
            'product',
            result[0].orderedproduct_set.first()._state.fields_cache.keys(),
            "Related Product has not been selected."
        )
        product_cache = result[0].orderedproduct_set.first() \
            .product._prefetched_objects_cache.keys(),
        self.assertIn(
            {'sale_set'},
            product_cache,
            "objects related to the product has not been prefetched."
        )

    def test_prefetch_images_and_reviews(self):
        result = self.selector._prefetch_data(
            orders_qs=models.Order.objects.all(),
            with_images_and_reviews=True,
            with_user_profile=False,
        )

        product_cache = result[0].orderedproduct_set.first() \
            .product._prefetched_objects_cache.keys()
        for expected in ("images", "review_set",):
            self.assertIn(
                expected,
                product_cache,
                f"Related {expected} has not been prefetched."
            )

    def test_prefetch_user_profile(self):
        result = self.selector._prefetch_data(
            orders_qs=models.Order.objects.all(),
            with_images_and_reviews=False,
            with_user_profile=True,
        )
        self.assertIn(
            "user",
            result[0]._state.fields_cache.keys(),
            "Related User has not been selected."
        )
        self.assertIn(
            "profile",
            result[0].user._state.fields_cache.keys(),
            "Related Profile has not been selected."
        )

    def test_prefetch_all_data(self):
        result = self.selector._prefetch_data(
            orders_qs=models.Order.objects.all(),
            with_images_and_reviews=True,
            with_user_profile=True,
        )

        # Assert that all related data is prefetched
        self.assertTrue(hasattr(result.first(), 'orderedproduct_set'))
        self.assertTrue(
            hasattr(result.first().orderedproduct_set.first(), 'product'))
        self.assertTrue(
            hasattr(result.first().orderedproduct_set.first().product,
                    'sale_set'))
        self.assertTrue(
            hasattr(result.first().orderedproduct_set.first().product,
                    'images'))
        self.assertTrue(
            hasattr(result.first().orderedproduct_set.first().product,
                    'review_set'))
        self.assertTrue(hasattr(result.first(), 'user'))
        self.assertTrue(hasattr(result.first().user, 'profile'))


class GetOneOrderTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_profile",
        "test_order",
        "test_product",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()

    def setUp(self) -> None:
        self.user = UserModel.objects.get(pk=1)
        self.order = models.Order.objects.create(user=self.user)

    def test_get_existing_order(self):
        result = self.selector.get_one_order_of_user(
            order_id=self.order.pk, user=self.user)

        self.assertIsNotNone(result)
        self.assertEqual(
            result, self.order, "Result does not match the expected order.")

    def test_get_nonexistent_order(self):
        result = self.selector.get_one_order_of_user(
            order_id=9999, user=self.user)

        self.assertIsNone(result)

    def test_get_order_of_different_user(self):
        user2 = UserModel.objects.create(username='otheruser')
        order2 = models.Order.objects.create(user=user2)

        result = self.selector.get_one_order_of_user(
            order_id=order2.pk, user=self.user)

        self.assertIsNone(result)


class GetEditingOrderTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()

    def setUp(self):
        self.user = UserModel.objects.get(pk=1)
        self.order = models.Order.objects.filter(
            user=self.user, status=models.Order.Statuses.EDITING).first()

    def test_get_editing_order(self):
        result = self.selector.get_editing_order_of_user(
            order_id=self.order.pk, user=self.user)

        self.assertIsNotNone(result)
        self.assertEqual(
            result, self.order, "Result does not match the expected order.")

    def test_get_nonediting_order(self):
        non_editing_order = models.Order.objects.create(
            user=self.user, status=models.Order.Statuses.CART)

        result = self.selector.get_editing_order_of_user(
            order_id=non_editing_order.pk, user=self.user, or_404=False, )

        self.assertIsNone(result)

    def test_get_nonexistent_order(self):
        result = self.selector.get_editing_order_of_user(
            order_id=9999, user=self.user, or_404=False)

        self.assertIsNone(result)

    def test_get_nonexistent_order_with_404(self):
        with self.assertRaises(Http404):
            self.selector.get_editing_order_of_user(
                order_id=9999, user=self.user, or_404=True)


@override_settings(
    BOUNDARY_OF_FREE_DELIVERY=100,
    EXPRESS_DELIVERY_EXTRA_CHARGE=10,
    ORDINARY_DELIVERY_COST=5,
)
class GetTotalCostTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product"
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d_conf_services.DynamicConfigService().set_default_config()
        cls.selector = selectors.OrderSelector()
        cls.boundary_free = settings.BOUNDARY_OF_FREE_DELIVERY
        cls.express_extra_charge = settings.EXPRESS_DELIVERY_EXTRA_CHARGE
        cls.ordinary_delivery_cost = settings.ORDINARY_DELIVERY_COST

    def setUp(self):
        self.user = UserModel.objects.get(pk=1)
        self.order = models.Order.objects.create(
            user=self.user,
            delivery_type=models.Order.DeliveryTypes.EXPRESS
        )
        self.price_1 = 50
        self.price_2 = 100
        self.ordered_product1 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=1,
            count=2,
            price=self.price_1,
        )
        self.ordered_product2 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=2,
            count=1,
            price=self.price_2,
        )

    def test_get_total_cost_with_express_delivery(self):
        result = self.selector.get_total_cost(order=self.order)

        # Expected total cost =
        # = (50*2 + 100*1){main} + 0{ordinary} + 10{express} = 210
        main_cost = (self.price_1 * 2) + self.price_2
        delivery_cost = self.express_extra_charge
        if main_cost < self.boundary_free:
            delivery_cost += self.ordinary_delivery_cost
        expected_total_cost = main_cost + delivery_cost

        self.assertEqual(
            result,
            expected_total_cost,
            "The result doesn't match the expected total cost."
        )

    def test_get_total_cost_with_ordinary_delivery(self):
        order_ordinary_delivery = models.Order.objects.create(
            user=self.user,
            delivery_type=models.Order.DeliveryTypes.ORDINARY,
        )
        models.OrderedProduct.objects.create(
            order=order_ordinary_delivery,
            product_id=1,
            count=1,
            price=self.price_1,
        )
        result = self.selector.get_total_cost(order=order_ordinary_delivery)

        # Expected total cost = 50{main} + 5{ordinary} = 55
        expected_total_cost = self.price_1 + self.ordinary_delivery_cost

        self.assertEqual(
            result,
            expected_total_cost,
            "The result doesn't match the expected total cost.",
        )


class GetOrderMainCostTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product"
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = selectors.OrderSelector()

    def setUp(self):
        self.user = UserModel.objects.get(pk=1)
        self.order = models.Order.objects.create(
            user=self.user
        )
        self.price_1 = 50
        self.price_2 = 100
        self.ordered_product1 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=1,
            count=2,
            price=self.price_1,
        )
        self.ordered_product2 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=2,
            count=1,
            price=self.price_2,
        )

    def test_get_order_main_cost(self):
        result = self.selector.get_order_main_cost(order=self.order)

        # Expected main cost = 2 * 50 + 1 * 100 = 200
        expected_main_cost = 2 * self.price_1 + self.price_2

        self.assertEqual(
            result,
            expected_main_cost,
            "The result doesn't match the expected total cost.",
        )


@override_settings(
    BOUNDARY_OF_FREE_DELIVERY=100,
    EXPRESS_DELIVERY_EXTRA_CHARGE=10,
    ORDINARY_DELIVERY_COST=5,
)
class GetDeliveryCostTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product"
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d_conf_services.DynamicConfigService().set_default_config()
        cls.selector = selectors.OrderSelector()
        cls.boundary_free = settings.BOUNDARY_OF_FREE_DELIVERY
        cls.express_extra_charge = settings.EXPRESS_DELIVERY_EXTRA_CHARGE
        cls.ordinary_delivery_cost = settings.ORDINARY_DELIVERY_COST

    def setUp(self):
        self.user = UserModel.objects.get(pk=1)
        self.order = models.Order.objects.create(
            user=self.user,
            delivery_type=models.Order.DeliveryTypes.EXPRESS
        )
        self.price_1 = 50
        self.price_2 = 100
        self.ordered_product1 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=1,
            count=2,
            price=self.price_1,
        )
        self.ordered_product2 = models.OrderedProduct.objects.create(
            order=self.order,
            product_id=2,
            count=1,
            price=self.price_2,
        )

    def test_get_delivery_cost_with_order(self):
        result = self.selector.get_delivery_cost(order=self.order)
        # Expected delivery cost = 10{express} + 0{ordinary over boundary}
        expected_delivery_cost = 10

        self.assertEqual(
            result,
            expected_delivery_cost,
            "The result doesn't match the expected total cost.",
        )

    def test_get_delivery_cost_with_main_cost_and_express_flag(self):
        # Test getting delivery cost using main cost and express flag
        result = self.selector.get_delivery_cost(
            main_cost=Decimal(99),
            is_express=True,
        )

        # Expected delivery cost = 10{express} + 5{ordinary}
        expected_delivery_cost = 5 + 10

        self.assertEqual(
            result,
            expected_delivery_cost,
            "The result doesn't match the expected total cost.",
        )

    def test_get_delivery_cost_with_invalid_args(self):
        with self.assertRaises(AttributeError):
            self.selector.get_delivery_cost(
                order=self.order, main_cost=Decimal(100), is_express=True)

    def test_get_delivery_cost_with_missing_args(self):
        with self.assertRaises(AttributeError):
            self.selector.get_delivery_cost(
                order=None, main_cost=None, is_express=None)
