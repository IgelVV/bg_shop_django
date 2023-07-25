from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from shop import serializers, models


class ProductPopularApiGetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:products_popular")

    @patch('shop.selectors.ProductSelector.get_popular_products')
    def test_get_popular_products(
            self,
            mock_get_popular_products,
    ):
        products = [
            models.Product(
                id=1,
                title="Popular Product 1",
            ),
            models.Product(
                id=2,
                title="Popular Product 2",
            ),
        ]
        mock_get_popular_products.return_value = products
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.ProductShortSerializer(products, many=True).data
        )
        mock_get_popular_products.assert_called_once_with()
