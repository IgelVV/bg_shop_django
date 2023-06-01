from typing import Type, Any

from collections import OrderedDict

from django.db import models as db_models
from django import views
from rest_framework import pagination, serializers, response
from rest_framework import request as drf_request


def get_paginated_response(
        *,
        pagination_class: Type[pagination.BasePagination],
        serializer_class: Type[serializers.Serializer],
        queryset: db_models.QuerySet,
        request: drf_request.Request,
        view: views.View,
) -> response.Response:
    """
    Sends DRF response with pagination, based on pagination_class
    and serializer_class. If page is None, sends serialized data directly.
    :param pagination_class: to create paginated queryset and paginated response
    :param serializer_class: to serialize passed queryset
    :param queryset: to serialize and paginate
    :param request: DRF request to get pagination params
    :param view: current view
    :return: DRF response
    """
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return response.Response(data=serializer.data)


class PageNumberPagination(pagination.PageNumberPagination):
    """For pagination based on pages. Adds fields to response
    to represent pagination"""
    page_size = 20

    def get_paginated_response(self, data: Any) -> response.Response:
        """
        Adds new fields to response
        :param data: main response data
        :return: modified response
        """
        return response.Response(OrderedDict([
            ('items', data),
            ("currentPage", self.page.number),
            ("lastPage", self.page.paginator.num_pages)
        ]))

    def get_paginated_data(self, data: Any) -> OrderedDict:
        """
        Adds new fields to data, without sending response.
        :param data: main data to send as response later
        :return: modified data
        """
        return OrderedDict([
            ('items', data),
            ("currentPage", self.page.number),
            ("lastPage", self.page.paginator.count)
        ])


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    """For pagination based on limit and offset.
    Tt is specified for current proj"""
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data: Any) -> OrderedDict:
        """
        Adds new fields to data, without sending response.
        :param data: main data to send as response later
        :return: modified data
        """
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data: Any) -> response.Response:
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return response.Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )