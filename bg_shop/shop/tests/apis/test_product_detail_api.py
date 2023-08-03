from collections import OrderedDict
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from shop import models
from shop.apis import ProductDetailApi


class ProductDetailApiOutputSerializerTestCase(TestCase):
    fixtures = [
        "test_category",
        "test_catalog",
        "test_user",
        "test_review",
        "test_tag",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = models.Product.objects.get(pk=1)

    def test_output_serializer(self):
        expected_data = {
            "id": 1,
            "category": 1,
            "price": Decimal('50.00'),
            "count": 21,
            "date": "2022-12-06",
            "title": "Test item 1",
            "description": "test description...",
            "fullDescription": "test description",
            "freeDelivery": True,
            "images": [],
            "tags": [
                OrderedDict([
                    ('id', 1),
                    ('name', 'test tag 1')
                ])
            ],
            "reviews": [
                OrderedDict([
                    ('author', 'test_user'),
                    ('email', ''),
                    ('text', 'best'),
                    ('rate', 10),
                    ('date', '10/Jun/2023')
                ]),
                OrderedDict([
                    ('author', 'test_user'),
                    ('email', ''),
                    ('text', '<h1>I like this game</h1>'),
                    ('rate', 9),
                    ('date', '19/Jun/2023'),
                ])
            ],
            "rating": 9.5,
        }

        serializer = ProductDetailApi.OutputSerializer(self.product)
        self.assertEqual(serializer.data, expected_data)

    def test_review_serializer(self):
        review_data = {
            "author": "test_user",
            "email": "",
            "text": "best",
            "rate": 10,
            "date": '10/Jun/2023',
        }
        review = models.Review.objects.get(pk=1)

        serializer = ProductDetailApi.OutputSerializer.ReviewSerializer(review)
        self.assertEqual(serializer.data, review_data)

    @patch("shop.selectors.ProductSelector.get_discounted_price")
    def test_get_price(self, mock_get_discounted_price):
        discounted_price = Decimal('80.00')
        mock_get_discounted_price.return_value = discounted_price

        price = ProductDetailApi.OutputSerializer().get_price(self.product)
        self.assertEqual(price, discounted_price)
        mock_get_discounted_price.assert_called_once_with(
            product=self.product,
            date=timezone.now().date()
        )

    @patch("shop.selectors.ProductSelector.is_free_delivery")
    def test_get_free_delivery(self, mock_is_free_delivery):
        mock_is_free_delivery.return_value = True

        free_delivery = ProductDetailApi.OutputSerializer().get_freeDelivery(
            self.product)
        self.assertTrue(free_delivery)
        mock_is_free_delivery.assert_called_once_with(self.product)

    @patch("shop.selectors.ProductSelector.get_rating")
    def test_get_rating(self, mock_get_rating):
        avg_rating = 4.56789
        mock_get_rating.return_value = avg_rating

        rating = ProductDetailApi.OutputSerializer().get_rating(self.product)
        self.assertEqual(rating, 4.57)
        mock_get_rating.assert_called_once_with(self.product.pk)


class ProductDetailApiGetTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = models.Product.objects.get(pk=1)
        cls.url = reverse("api:shop:product-detail", args=[cls.product.pk])

    @patch('shop.selectors.ProductSelector.get_discounted_price')
    @patch('shop.selectors.ProductSelector.is_free_delivery')
    @patch('shop.selectors.ProductSelector.get_rating')
    def test_get(
            self,
            mock_get_rating,
            mock_is_free_delivery,
            mock_get_discounted_price,
    ):
        mock_is_free_delivery.return_value = True
        mock_get_discounted_price.return_value = Decimal('100.00')
        mock_get_rating.return_value = None

        expected_data = {
            'id': 1,
            'category': None,
            'price': Decimal('100.00'),
            'count': 21,
            'date': '2022-12-06',
            'title': 'Test item 1',
            'description': 'test description...',
            'fullDescription': 'test description',
            'freeDelivery': True,
            'images': [],
            'tags': [],
            'reviews': [],
            'rating': None,
        }

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            expected_data,
        )
        mock_get_discounted_price.assert_called_once_with(
            product=self.product,
            date=timezone.now().date(),
        )
        mock_is_free_delivery.assert_called_once_with(self.product)
        mock_get_rating.assert_called_once_with(self.product.pk)
