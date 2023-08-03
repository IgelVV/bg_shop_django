from collections import OrderedDict

from django.test import TestCase
from rest_framework import serializers, permissions
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from api.pagination import (
    LimitOffsetPagination,
    get_paginated_response,
)
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class ExampleListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 1

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserModel
            fields = ("id", "username")

    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        queryset = UserModel.objects.order_by("id")

        response = get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

        return response


class GetPaginatedResponseTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user1 = UserModel.objects.create_user(username="user1")
        self.user2 = UserModel.objects.create_user(username="user2")

    def test_response_is_paginated_correctly(self):
        first_page_request = self.factory.get("/some/path")
        first_page_response = ExampleListApi.as_view()(first_page_request)

        expected_first_page_response = OrderedDict(
            {
                "limit": 1,
                "offset": 0,
                "count": UserModel.objects.count(),
                "next": "http://testserver/some/path?limit=1&offset=1",
                "previous": None,
                "results": [
                    OrderedDict(
                        {
                            "id": self.user1.id,
                            "username": self.user1.username,
                        }
                    )
                ],
            }
        )

        self.assertEqual(
            expected_first_page_response,
            first_page_response.data,
            "Wrong paginated response.",
        )

        next_page_request = self.factory.get("/some/path?limit=1&offset=1")
        next_page_response = ExampleListApi.as_view()(next_page_request)

        expected_next_page_response = OrderedDict(
            {
                "limit": 1,
                "offset": 1,
                "count": UserModel.objects.count(),
                "next": None,
                "previous": "http://testserver/some/path?limit=1",
                "results": [
                    OrderedDict(
                        {
                            "id": self.user2.id,
                            "username": self.user2.username,
                        }
                    )
                ],
            }
        )

        self.assertEqual(
            expected_next_page_response,
            next_page_response.data,
            "Wrong paginated response.",
        )
