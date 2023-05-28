from collections import OrderedDict

from rest_framework import serializers, status, permissions, views
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
            # means `only free delivery` (if False - select all)
            freeDelivery = serializers.BooleanField(required=False, allow_null=True)
            available = serializers.BooleanField(required=False, allow_null=True)

        # it's better to remove nested query params and rewrite frontend
        filter = FilterSerializer(required=False, allow_null=True,)
        currentPage = serializers.IntegerField(required=False, allow_null=True)
        sort = serializers.ChoiceField(
            choices=[
                "rating",
                "price",
                "reviews",
                "date",
                "title",
                "popularity"
            ],
            required=False,
            allow_blank=True)
        sortType = serializers.CharField(required=False, allow_blank=True)
        limit = serializers.IntegerField(required=False, allow_null=True)
        category = serializers.IntegerField(required=False)
        tags = serializers.ListField(child=serializers.IntegerField(), required=False)

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """

        :param request:
        :return:
        """
        selector = selectors.ProductSelector()
        output_serializer = shop_serializers.ProductShortSerializer
        params = api_utils.parse_query_params_square_brackets(request)
        params_serializer = self.QueryParamsSerializer(data=params)
        params_serializer.is_valid(raise_exception=True)
        validated_params = params_serializer.validated_data

        filter_params = (
            validated_params.get('filter', None)
            or OrderedDict()
        )
        if category := validated_params.get('category', None):
            filter_params['category'] = category
        if tags := validated_params.get('tags', None):
            filter_params['tags'] = tags

        catalog = selector.get_catalog(
            filters=filter_params,
            sort_field=validated_params.get("sort", None),
            order=validated_params.get("sortType", None),
        )

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=output_serializer,
            queryset=catalog,
            request=request,
            view=self,
        )
