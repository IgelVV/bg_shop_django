import json
from decimal import Decimal
from collections import OrderedDict
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from rest_framework import status, response as drf_response
from rest_framework.test import APIRequestFactory

from shop import serializers as shop_serializers
from shop.apis import CatalogApi


class ComparableRequest:
    def __init__(self, request):
        self.request = request

    def __eq__(self, other):
        return self.request.get_full_path() == other.get_full_path()

    def __ne__(self, other):
        return self.request.get_full_path() != other.get_full_path()


class ComparableCatalogApiInstance:
    def __eq__(self, other):
        return isinstance(other, CatalogApi)

    def __ne__(self, other):
        return not isinstance(other, CatalogApi)


class CatalogApiGetTestCase(TestCase):
    fixtures = [
        "test_catalog",
        "test_category",
        "test_tag",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:catalog")

    @patch('shop.selectors.ProductSelector.get_catalog')
    @patch('api.pagination.get_paginated_response')
    def test_get(
            self,
            mock_get_paginated_response,
            mock_get_catalog,
    ):
        params = {
            'filter[name]': 'Test',
            'filter[minPrice]': 0,
            'filter[maxPrice]': 50,
            'currentPage': 1,
            'tags[]': [2],
            'limit': 20
        }
        mock_parsed_params = {
            'filter':
                OrderedDict([
                    ('name', 'Test'),
                    ('minPrice', 0),
                    ('maxPrice', 50),
                    ('tags', [2])
                ]),
            'currentPage': '1',
            'tags': ['2'],
            'limit': '20'
        }

        mock_get_paginated_response.return_value = drf_response.Response(
            status=200)

        factory = APIRequestFactory()
        request = factory.get(self.url, data=params)

        view = CatalogApi.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_get_catalog.assert_called_once_with(
            filters=mock_parsed_params['filter'],
            sort_field=None,
            order=None,
        )
        mock_get_paginated_response.assert_called_once_with(
            pagination_class=CatalogApi.Pagination,
            serializer_class=shop_serializers.ProductShortSerializer,
            queryset=mock_get_catalog(),
            request=ComparableRequest(request=request),
            view=ComparableCatalogApiInstance(),
        )

    def test_integration(self):
        params = {
            'filter[name]': 'Test',
            'filter[minPrice]': 0,
            'filter[maxPrice]': 50,
            'currentPage': 1,
            'tags[]': [2],
            'limit': 20
        }
        expected_data = OrderedDict([
            ('items', [
                OrderedDict([
                    ('id', 2),
                    ('category', 2),
                    ('price', Decimal('40.00')),
                    ('count', 121),
                    ('date', '2022-12-08'),
                    ('title', 'Test item 2'),
                    ('description', 'test description 2...'),
                    ('freeDelivery', True),
                    ('images', []),
                    ('tags', [
                        OrderedDict([
                            ('id', 1),
                            ('name', 'test tag 1')
                        ]),
                        OrderedDict([
                            ('id', 2),
                            ('name', 'test tag 2')
                        ])
                    ]),
                    ('reviews', 0),
                    ('rating', None)
                ]),
            ]),
            ('currentPage', 1),
            ('lastPage', 1)
        ])

        response = self.client.get(self.url, data=params)
        self.assertEqual(response.data, expected_data)


class QueryParamsSerializerTestCase(TestCase):
    def test_valid_data(self):
        data = {
            'filter': {
                'name': 'Test',
                'minPrice': 0,
                'maxPrice': 50000,
                'freeDelivery': True,
                'available': False,
            },
            'currentPage': 1,
            'sort': 'rating',
            'sortType': 'asc',
            'limit': 20,
            'category': 1,
            'tags': [1, 2, 3],
        }
        serializer = CatalogApi.QueryParamsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)

    def test_invalid_data(self):
        data = {
            'filter': {
                'name': 'Test',
                'minPrice': -1,  # Invalid value but unchecked
                'maxPrice': 50000,
                'freeDelivery': 'Invalid',  # Invalid value
                'available': False,
            },
            'currentPage': 'Invalid',  # Invalid value
            'sort': 'invalid_sort',  # Invalid value
            'sortType': 'asc',
            'limit': 20,
            'category': 'Invalid',  # Invalid value
            'tags': [1, 'Invalid', 3],  # Invalid value
        }
        serializer = CatalogApi.QueryParamsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        expected_errors = {
            'filter': {
                'freeDelivery': ['Must be a valid boolean.'],
            },
            'currentPage': ['A valid integer is required.'],
            'sort': ['"invalid_sort" is not a valid choice.'],
            'category': ['A valid integer is required.'],
            'tags': {
                '1': ['A valid integer is required.'],
            },
        }
        self.assertEqual(
            json.loads(json.dumps(serializer.errors)),
            expected_errors,
        )
