from rest_framework import serializers, status, permissions, views, generics
from rest_framework import exceptions as drf_exceptions
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from shop import models, services, selectors
from common import serializers as common_serializers


class CategoryApi(views.APIView):
    class OutputSerializer(serializers.ModelSerializer):
        subcategories = serializers.SerializerMethodField()
        image = common_serializers.ImageSerializer(allow_null=True)

        def get_subcategories(self, obj):
            if subcategories := obj.category_set:
                return CategoryApi.OutputSerializer(
                    subcategories, many=True,).data
            else:
                return None

        class Meta:
            model = models.Category
            fields = ("id", "title", "image", "subcategories")
            depth = 10

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        categories = selectors.CategorySelector.get_root_categories_queryset()
        serializer = self.OutputSerializer(
            instance=categories, many=True)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)
