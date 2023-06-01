from decimal import Decimal

from rest_framework import permissions, views
from rest_framework import serializers as drf_serializers
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from api import pagination
from shop import models, selectors
from common import serializers as common_serializers


class SalesApi(views.APIView):
    """Represents all active sales"""
    class Pagination(pagination.PageNumberPagination):
        page_query_param = "currentPage"
        page_size = 20

    class OutputSerializer(drf_serializers.Serializer):
        """For Sale model"""
        id = drf_serializers.IntegerField(source="product.id")
        price = drf_serializers.DecimalField(max_digits=8, decimal_places=2, source="product.price")
        salePrice = drf_serializers.SerializerMethodField()
        dateFrom = drf_serializers.DateField(source="date_from")
        dateTo = drf_serializers.DateField(source="date_to")
        title = drf_serializers.CharField(source="product.title")
        images = common_serializers.ImageSerializer(source="product.images", many=True)

        def get_salePrice(self, obj: models.Sale) -> Decimal:
            """Price after discount"""
            original_price = obj.product.price
            sale_price = Decimal(1 - obj.discount * 0.01) * original_price
            sale_price = round(sale_price, 2)
            return sale_price

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """
        Returns information about current sales (products with discount)
        :param request: drf request
        :return: paginated response
        """
        selector = selectors.SaleSelector()
        sales = selector.get_sales()

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=sales,
            request=request,
            view=self,
        )
