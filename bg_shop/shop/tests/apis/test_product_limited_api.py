from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from shop import serializers, models


class ProductLimitedApiGetTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:products_limited")

    @patch('shop.selectors.ProductSelector.get_limited_products')
    def test_get_limited_products(
            self,
            mock_get_limited_products,
    ):
        products = models.Product.objects.filter(
            limited_edition=True, is_active=True)
        products = products[:settings.LIMITED_PRODUCTS_LIMIT]
        mock_get_limited_products.return_value = products

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.ProductShortSerializer(products, many=True).data
        )
        mock_get_limited_products.assert_called_once_with()
