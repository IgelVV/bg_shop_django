from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from shop import models, selectors
from common import serializers as common_serializers


class CategoryApi(views.APIView):
    """
    For representing of Category tree in a header.
    """
    class OutputSerializer(serializers.ModelSerializer):
        """Recursive structure of categories"""
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
        """
        Returns tree of categories and subcategories.
        :param request: request
        :return: drf response
        """
        selector = selectors.CategorySelector()
        categories = selector.get_root_categories_queryset()
        serializer = self.OutputSerializer(
            instance=categories, many=True)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)
