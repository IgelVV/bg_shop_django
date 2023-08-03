from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status, response as drf_response
from rest_framework.test import APIRequestFactory

from shop.models import Sale
from shop.apis import SalesApi


class ComparableRequest:
    def __init__(self, request):
        self.request = request

    def __eq__(self, other):
        return self.request.get_full_path() == other.get_full_path()

    def __ne__(self, other):
        return self.request.get_full_path() != other.get_full_path()


class ComparableSalesApiInstance:
    def __eq__(self, other):
        return isinstance(other, SalesApi)

    def __ne__(self, other):
        return not isinstance(other, SalesApi)


class SalesApiGetTestCase(TestCase):
    fixtures = [
        "test_product",
        "test_sale",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("api:shop:sales")

    @patch('shop.selectors.SaleSelector.get_sales')
    @patch('api.pagination.get_paginated_response')
    def test_get_sales(
            self,
            mock_get_paginated_response,
            mock_get_sales,
    ):
        sales = Sale.objects.all()
        mock_get_sales.return_value = sales
        mock_get_paginated_response.return_value = \
            drf_response.Response(status=200)

        factory = APIRequestFactory()
        request = factory.get(self.url)

        view = SalesApi.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_sales.assert_called_once()
        mock_get_paginated_response.assert_called_once_with(
            pagination_class=SalesApi.Pagination,
            serializer_class=SalesApi.OutputSerializer,
            queryset=sales,
            request=ComparableRequest(request),
            view=ComparableSalesApiInstance(),
        )


class SalesApiOutputSerializerTestCase(TestCase):
    fixtures = [
        "test_product",
    ]

    def test_serialize_data(self):
        sale = Sale.objects.create(
            product_id=1, discount=20, date_from="2023-01-01",
            date_to="2023-01-31"
        )
        expected_data = {
            "id": 1,
            "price": "50.00",
            "salePrice": Decimal("40.00"),
            "dateFrom": "2023-01-01",
            "dateTo": "2023-01-31",
            "title": "Test item 1",
            "images": [],
        }

        serializer = SalesApi.OutputSerializer(instance=sale)
        self.assertEqual(serializer.data, expected_data)

    def test_get_salePrice(self):
        sale = Sale.objects.create(
            product_id=1, discount=20, date_from="2023-01-01",
            date_to="2023-01-31"
        )

        serializer = SalesApi.OutputSerializer(instance=sale)
        sale_price = serializer.data.get("salePrice")
        self.assertEqual(sale_price, Decimal("40.00"))
