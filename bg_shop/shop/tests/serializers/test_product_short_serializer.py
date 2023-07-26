from unittest.mock import MagicMock, patch, PropertyMock
from collections import OrderedDict
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from shop.models import Product, Review
from shop.serializers import ProductShortSerializer

UserModel = get_user_model()


class ProductShortSerializerTestCase(TestCase):
    boundary = 20

    fixtures = [
        "test_product"
    ]

    def test_get_price(self):
        serializer = ProductShortSerializer()
        product = Product.objects.get(pk=1)
        result = serializer.get_price(product)

        self.assertEqual(result, Decimal('50.00'))

    @patch(
        "dynamic_config.selectors.DynamicConfigSelector"
        ".boundary_of_free_delivery",
        new_callable=PropertyMock,
        return_value=boundary,
    )
    def test_get_freeDelivery_with_boundary(self, mock_boundary):
        serializer = ProductShortSerializer()
        product = Product.objects.get(pk=1)

        result = serializer.get_freeDelivery(product)

        self.assertTrue(result)

    @patch(
        "dynamic_config.selectors.DynamicConfigSelector"
        ".boundary_of_free_delivery",
        new_callable=PropertyMock,
        return_value=None,
    )
    def test_get_freeDelivery_without_boundary(self, mock_boundary):
        serializer = ProductShortSerializer()
        product = Product.objects.get(pk=1)

        result = serializer.get_freeDelivery(product)

        self.assertFalse(result)

    def test_get_reviews_with_reviews(self):
        serializer = ProductShortSerializer()

        mock_review_set = MagicMock()
        mock_product = MagicMock(review_set=mock_review_set)
        result = serializer.get_reviews(mock_product)

        self.assertEqual(result, mock_review_set.count())

    def test_get_reviews_without_reviews(self):
        serializer = ProductShortSerializer()
        product = Product.objects.get(pk=1)
        result = serializer.get_reviews(product)

        self.assertEqual(result, 0)

    def test_get_rating_with_reviews(self):
        serializer = ProductShortSerializer()
        user = UserModel.objects.create_user(
            username="test",
            password="",
        )
        product = Product.objects.get(pk=1)

        Review.objects.create(product=product, rate=4, author=user)
        Review.objects.create(product=product, rate=5, author=user)

        serializer.review_set = MagicMock(spec=Review.objects)
        serializer.review_set.count.return_value = 2
        result = serializer.get_rating(product)
        self.assertEqual(result, 4.5)

    def test_get_rating_with_no_reviews(self):
        serializer = ProductShortSerializer()
        product = Product.objects.get(pk=1)

        serializer.review_set = MagicMock(spec=Review.objects)
        serializer.review_set.count.return_value = 0
        result = serializer.get_rating(product)
        self.assertIsNone(result)


class GeneralProductSerializationTestCase(TestCase):
    fixtures = [
        "test_user",
        "test_catalog",
        "test_category",
        "test_review",
        "test_tag",
    ]

    @patch("dynamic_config.selectors.DynamicConfigSelector"
           ".boundary_of_free_delivery", new_callable=PropertyMock)
    def test_product_serialization(self, mock_boundary):
        mock_boundary.return_value = 20

        product = Product.objects.get(pk=1)
        expected_data = {
            "id": product.id,
            "category": product.category_id,
            "price": Decimal(product.price),
            "count": product.count,
            "date": str(product.release_date),
            "title": product.title,
            "description": product.short_description,
            "freeDelivery": True,
            "images": [],
            "tags": [OrderedDict([('id', 1), ('name', 'test tag 1')])],
            "reviews": product.review_set.count(),
            "rating": 9.5,
        }

        serializer = ProductShortSerializer(product)
        self.assertEqual(serializer.data, expected_data)
