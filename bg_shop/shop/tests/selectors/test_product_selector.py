from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, PropertyMock

from django.test import TestCase, override_settings
from django.conf import settings
from django.db.models import QuerySet

from shop.models import Product, Review, Sale
from shop.selectors import ProductSelector
from orders import models as order_models


class GetActiveProductsTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    def test_get_active_products(self):
        selector = ProductSelector()
        queryset = selector.get_active_products()
        expected_result = Product.objects.filter(is_active=True)

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )


class IsAvailableTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    def test_is_available_with_product_object(self):
        product = Product.objects.get(pk=1)
        result = self.selector.is_available(product=product)

        self.assertTrue(result)

    def test_is_available_with_product_id(self):
        product_id = 1
        result = self.selector.is_available(product_id=product_id)

        self.assertTrue(result)

    def test_unavailable(self):
        product = Product(is_active=False, count=0)
        result = self.selector.is_available(product=product)
        self.assertFalse(result)

    def test_is_available_with_both_product_and_product_id_raises_error(self):
        product = Product.objects.get(pk=1)
        product_id = 1

        with self.assertRaises(AttributeError):
            self.selector.is_available(product=product, product_id=product_id)

    def test_is_available_with_no_arguments_raises_error(self):
        with self.assertRaises(AttributeError):
            self.selector.is_available()


class GetRatingTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_product",
        "test_review",
    ]

    def test_get_rating(self):
        selector = ProductSelector()
        product_id = 1
        result = selector.get_rating(product_id)

        self.assertAlmostEqual(result, 9.5)


class IsFreeDeliveryTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    @patch(
        'dynamic_config.selectors.DynamicConfigSelector'
        '.boundary_of_free_delivery',
        new_callable=PropertyMock,
    )
    def test_is_free_delivery_with_boundary(
            self,
            mock_boundary_of_free_delivery,
    ):
        mock_boundary_of_free_delivery.return_value = 51
        product = Product.objects.get(pk=1)

        result = self.selector.is_free_delivery(product)

        self.assertFalse(result)
        mock_boundary_of_free_delivery.assert_called_once()

    @patch(
        'dynamic_config.selectors.DynamicConfigSelector'
        '.boundary_of_free_delivery',
        new_callable=PropertyMock,
    )
    def test_is_free_delivery_without_boundary(
            self,
            mock_boundary_of_free_delivery,
    ):
        mock_boundary_of_free_delivery.return_value = None
        product = Product.objects.get(pk=1)

        result = self.selector.is_free_delivery(product)

        self.assertFalse(result)
        mock_boundary_of_free_delivery.assert_called_once()


class GetCatalogTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    @patch("shop.filters.BaseProductFilter")
    @patch('shop.selectors.ProductSelector'
           '._prefetch_for_product_short_serializer')
    @patch('shop.selectors.ProductSelector._sort_catalog')
    @patch('shop.selectors.ProductSelector.get_active_products')
    def test_get_catalog_without_filters_and_sort(
            self,
            mock_get_active,
            mock_sort,
            mock_prefetch,
            mock_filter,
    ):
        queryset = self.selector.get_catalog()

        self.assertEqual(queryset, mock_filter.return_value.qs)

        mock_get_active.assert_called_once_with()
        mock_prefetch.assert_called_once_with(
            query_set=mock_get_active.return_value)
        mock_filter.assert_called_once_with(
            data={}, queryset=mock_prefetch.return_value)
        mock_sort.assert_not_called()

    @patch("shop.filters.BaseProductFilter")
    @patch('shop.selectors.ProductSelector'
           '._prefetch_for_product_short_serializer')
    @patch('shop.selectors.ProductSelector._sort_catalog')
    @patch('shop.selectors.ProductSelector.get_active_products')
    def test_get_catalog_with_filters(
            self,
            mock_get_active,
            mock_sort,
            mock_prefetch,
            mock_filter,
    ):
        filters = {
            "name": "Product 1"
        }

        queryset = self.selector.get_catalog(filters=filters)

        self.assertEqual(queryset, mock_filter.return_value.qs)

        mock_get_active.assert_called_once_with()
        mock_prefetch.assert_called_once_with(
            query_set=mock_get_active.return_value)
        mock_filter.assert_called_once_with(
            data=filters, queryset=mock_prefetch.return_value)
        mock_sort.assert_not_called()

    @patch("shop.filters.BaseProductFilter")
    @patch('shop.selectors.ProductSelector'
           '._prefetch_for_product_short_serializer')
    @patch('shop.selectors.ProductSelector._sort_catalog')
    @patch('shop.selectors.ProductSelector.get_active_products')
    def test_get_catalog_with_sort(
            self,
            mock_get_active,
            mock_sort,
            mock_prefetch,
            mock_filter,
    ):
        sort_field = "price"
        order = "dec"

        queryset = self.selector.get_catalog(
            sort_field=sort_field, order=order)

        self.assertEqual(queryset, mock_sort.return_value)

        mock_get_active.assert_called_once_with()
        mock_prefetch.assert_called_once_with(
            query_set=mock_get_active.return_value)
        mock_filter.assert_called_once_with(
            data={}, queryset=mock_prefetch.return_value)
        mock_sort.assert_called_once_with(
            query_set=mock_filter.return_value.qs,
            sort_field=sort_field,
            order=order
        )


class PrefetchForProductShortSerializerTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    def test_prefetch_for_product_short_serializer(self):
        products = Product.objects.all()
        queryset = self.selector._prefetch_for_product_short_serializer(
            products)
        prefetched_obj = queryset.first()._prefetched_objects_cache
        self.assertIn("review_set", prefetched_obj)
        self.assertIn("images", prefetched_obj)
        self.assertIn("tags", prefetched_obj)
        self.assertIn("sale_set", prefetched_obj)


class SortCatalogTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_order",
        "test_product",
        "test_review",
        "test_ordered_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    def test_sort_by_rating_desc(self):
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="rating",
            order="dec",
        )
        self.assertListEqual(
            list(queryset.values_list("rating", flat=True)),
            [9.5, 7.0, 5.0, None]
        )

    def test_sort_by_price_asc(self):
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="price",
            order="inc",
        )
        self.assertListEqual(
            list(queryset.values_list("price", flat=True)),
            [
                Decimal("10.00"),
                Decimal("40.00"),
                Decimal("50.00"),
                Decimal("150.00")
            ]
        )

    def test_sort_by_reviews_default_order(self):
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="reviews",
        )
        self.assertListEqual(
            list(queryset.values_list("reviews", flat=True)),
            [2, 1, 1, 0]
        )

    def test_sort_by_date(self):
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="date",
        )
        self.assertListEqual(
            list(queryset.values_list("date", flat=True)),
            [
                date(2022, 12, 8),
                date(2022, 12, 8),
                date(2022, 12, 6),
                date(2022, 11, 6),
            ]
        )

    def test_sort_by_title(self):
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="title",
        )
        self.assertListEqual(
            list(queryset.values_list("title", flat=True)),
            ['Test item 4', 'Test item 3', 'Test item 2', 'Test item 1']
        )

    def test_sort_catalog_by_popularity(self):
        orders = order_models.Order.objects.filter(pk__in=[1, 2])
        for order in orders:
            order.status = order_models.Order.Statuses.COMPLETED
            order.save()
        queryset = self.selector._sort_catalog(
            Product.objects.all(),
            sort_field="popularity",
        )
        self.assertEqual(
            list(queryset.values_list("popularity", flat=True)),
            [6, 4, None, None]
        )

    def test_wrong_order_arg_rises_exception(self):
        with self.assertRaises(ValueError):
            self.selector._sort_catalog(
                Product.objects.all(),
                sort_field="title",
                order="Wrong"
            )


class GetProductsInBannersTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_banner",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    @patch('shop.selectors.ProductSelector'
           '._prefetch_for_product_short_serializer')
    def test_get_products_in_banners(
            self,
            mock_prefetch,
    ):
        mock_prefetch.side_effect = lambda query_set: query_set
        queryset = self.selector.get_products_in_banners()
        expected_result = Product.objects.filter(banner__isnull=False)

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            set(expected_result.values_list("id", flat=True))
        )
        mock_prefetch.assert_called_once()


@override_settings(POPULAR_PRODUCTS_LIMIT=2)
class GetPopularProductsTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    @patch('shop.selectors.ProductSelector.get_catalog')
    def test_get_popular_products(
            self,
            mock_get_catalog,
    ):
        mock_get_catalog.return_value = Product.objects.all()
        queryset = self.selector.get_popular_products()

        self.assertEqual(queryset.count(), 2)
        mock_get_catalog.assert_called_once_with(
            sort_field='popularity'
        )


@override_settings(LIMITED_PRODUCTS_LIMIT=1)
class GetLimitedProductsTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    @patch('shop.selectors.ProductSelector'
           '._prefetch_for_product_short_serializer')
    @patch('shop.selectors.ProductSelector.get_active_products')
    def test_get_limited_products(
            self,
            mock_get_active,
            mock_prefetch,
    ):
        mock_get_active.return_value = Product.objects.all()
        mock_prefetch.side_effect = lambda query_set: query_set
        queryset = self.selector.get_limited_products()

        self.assertEqual(queryset.count(), 1),
        self.assertTrue(queryset[0].limited_edition),
        mock_get_active.assert_called_once_with()
        mock_prefetch.assert_called_once()


class GetDiscountedPriceTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_sale",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selector = ProductSelector()

    def test_get_discounted_price_with_active_sale(self):
        product = Product.objects.get(pk=1)
        discounted_price = self.selector.get_discounted_price(
            product=product,
            date=date(2023, 7, 19),  # sale id=5
        )
        self.assertEqual(discounted_price, Decimal("42.00"))

    def test_get_discounted_price_without_active_sale(self):
        product = Product.objects.get(pk=2)
        discounted_price = self.selector.get_discounted_price(
            product=product,
            date=date(2023, 7, 19),
        )

        self.assertEqual(discounted_price, Decimal("40"))
