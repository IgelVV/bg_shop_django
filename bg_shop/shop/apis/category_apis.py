from rest_framework import serializers, status, permissions, views
from rest_framework import exceptions as drf_exceptions
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from shop import models


class CategoryApi(views.APIView):
    # class OutputSerializer(serializers.Serializer):
    #     class ImageSerializer(serializers.Serializer):
    #         src = serializers.CharField()
    #         alt = serializers.CharField(max_length=255)
    #
    #     id = serializers.IntegerField()
    #     title = serializers.CharField(max_length=255)
    #     image = ImageSerializer()
    #     subcategories = serializers.SerializerMethodField()
    #
    #     def get_subcategories(self, obj):
    #         if obj.subcategories is not None:
    #             return CategoryApi.OutputSerializer(obj.subcategories, many=True).data
    #         else:
    #             return None

    class OutputSerializer(serializers.ModelSerializer):
        subcategories = serializers.SerializerMethodField()

        def get_subcategories(self, obj):
            if subcategories := obj.category_set:
                return CategoryApi.OutputSerializer(
                    subcategories, many=True,).data
            else:
                return None

        class Meta:
            model = models.Category
            fields = ("id", "title","image", "subcategories")
            depth = 10

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        from django.forms.models import model_to_dict
        categories = models.Category.objects.select_related().all()
        # categories = model_to_dict(categories)
        # print(categories)
        serializer = self.OutputSerializer(
            instance=categories, many=True)
        # serializer.is_valid()
        # print(serializer.data)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)
