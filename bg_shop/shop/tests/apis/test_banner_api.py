import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from rest_framework import status
from rest_framework.test import APIRequestFactory

from shop.apis import BannerApi


class BannerApiGetTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_banner",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('api:shop:banners')

    # @patch('shop.selectors.ProductSelector')
    def test_user_is_anonymous(self, ):
        expected_data = [
            {
                'id': 1,
                'category': None,
                'price': 50.00,
                'count': 21,
                'date': '2022-12-06',
                'title': 'Test item 1',
                'description': 'test description...',
                'freeDelivery': True,
                'images': [],
                'tags': [],
                'reviews': 0,
                'rating': None
            },
            {
                'id': 2,
                'category': None,
                'price': 40.00,
                'count': 121,
                'date': '2022-12-08',
                'title': 'Test item 2',
                'description': 'test description 2...',
                'freeDelivery': True,
                'images': [],
                'tags': [],
                'reviews': 0,
                'rating': None
            }
        ]

        self.client.user = AnonymousUser()
        response = self.client.get(self.url)
        response.render()
        self.assertContains(
            response,
            json.dumps(expected_data, separators=(',', ':')),
        )

    @patch('shop.selectors.ProductSelector.get_products_in_banners')
    @patch('shop.serializers.ProductShortSerializer')
    def test_get_method(self, mock_serializer, mock_get_products):
        test_data = [
            {'id': 1, 'title': 'Banner Product 1'},
            {'id': 2, 'title': 'Banner Product 2'},
        ]
        mock_get_products.return_value = test_data
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = test_data
        factory = APIRequestFactory()
        request = factory.get(reverse('api:shop:banners'))
        view = BannerApi.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, mock_serializer_instance.data)
        mock_get_products.assert_called_once_with()
        mock_serializer.assert_called_once_with(instance=test_data, many=True)
