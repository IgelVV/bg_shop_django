from rest_framework import serializers, status, permissions, views, filters
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from api import utils as api_utils
from api import pagination
from shop import models, selectors, services
from shop import serializers as shop_serializers
from common import serializers as common_serializers


class CatalogApi(views.APIView):
    """"""
    class Pagination(pagination.PageNumberPagination):
        page_query_param = "currentPage"
        page_size_query_param = "limit"
        max_page_size = 50

    class QueryParamsSerializer(serializers.Serializer):
        class FilterSerializer(serializers.Serializer):
            name = serializers.CharField(required=False, allow_blank=True)
            minPrice = serializers.IntegerField(required=False, allow_null=True)
            maxPrice = serializers.IntegerField(required=False, allow_null=True)
            freeDelivery = serializers.BooleanField(required=False, allow_null=True)
            available = serializers.BooleanField(required=False, allow_null=True)

        filter = FilterSerializer(required=False, allow_null=True, )
        currentPage = serializers.IntegerField(required=False, allow_null=True)
        sort = serializers.ChoiceField(
            choices=["rating", "price", "reviews", "date"],
            required=False,
            allow_blank=True)
        sortType = serializers.CharField(required=False, allow_blank=True)
        limit = serializers.IntegerField(required=False, allow_null=True)
        # tags
        # category


    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """

        :param request:
        :return:
        """

        selector = selectors.ProductSelector()
        output_serializer = shop_serializers.ProductShortSerializer
        params = api_utils.nested_query_params_parser(request)
        query_params_serializer = self.QueryParamsSerializer(data=params)

        query_params_serializer.is_valid(raise_exception=True)
        query_params_serializer.validated_data['filter']["category"]=1
        # print(query_params_serializer.validated_data)
        # catalog = selector.get_catalog(filters=query_params_serializer.validated_data)
        catalog = selector.get_catalog() # add sort and filter by category

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=output_serializer,
            queryset=catalog,
            request=request,
            view=self,
        )
