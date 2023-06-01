from collections import OrderedDict

from rest_framework import serializers, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from api import utils as api_utils
from api import pagination
from shop import selectors
from shop import serializers as shop_serializers


class CatalogApi(views.APIView):
    """
    For getting all active products with using filters and sort params.
    """
    class Pagination(pagination.PageNumberPagination):
        page_query_param = "currentPage"
        page_size_query_param = "limit"
        max_page_size = 50

    class QueryParamsSerializer(serializers.Serializer):
        """
        Describes the expected query parameters.
        """
        class FilterSerializer(serializers.Serializer):
            # todo It needs to be changed to simplify.
            """Params for filtering results"""
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
        # it is filter param too
        category = serializers.IntegerField(required=False)
        tags = serializers.ListField(child=serializers.IntegerField(), required=False)

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """
        Filters must be nested in `filter` url query param using
        square brackets notation.
        Example of query string params:
            /?filter[name]=&filter[minPrice]=0&filter[maxPrice]=50000&
            currentPage=1&tags[]=6&tags[]=7&tags[]=8&limit=20
        :param request: drf request that may contain query params
            to filter, sort or paginate
        :return: paginated response
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
