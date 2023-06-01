from typing import Optional

from rest_framework import status, permissions, views
from rest_framework import serializers as drf_serializers
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.shortcuts import get_object_or_404

from shop import models, selectors, serializers
from common import serializers as common_serializers


class ProductDetailApi(views.APIView):
    """Detailed view of each product."""

    class OutputSerializer(drf_serializers.ModelSerializer):
        """Represents full information about product.
        It is used only in this view.
        It looks like ProductShortSerializer, but here are few differences:
        fullDescription - new field,
        reviews - represents all Review objects related to this Product.
        """
        class Meta:
            model = models.Product
            fields = (
                "id",
                "category",
                "price",
                "count",
                "date",
                "title",
                "description",
                "fullDescription",
                "freeDelivery",
                "images",
                "tags",
                "reviews",
                "rating",
            )
            depth = 1

        class ReviewSerializer(drf_serializers.Serializer):
            author = drf_serializers.CharField(max_length=150)  # username
            email = drf_serializers.SerializerMethodField()
            text = drf_serializers.CharField(max_length=5120)
            rate = drf_serializers.IntegerField()
            date = drf_serializers.DateTimeField(format="%d/%b/%Y")

            def get_email(self, obj: models.Review) -> str:
                """Email of author of review"""
                return obj.author.email

        category = drf_serializers.IntegerField(source='category_id')
        date = drf_serializers.DateField(source='release_date')
        description = drf_serializers.CharField(source='short_description')
        fullDescription = drf_serializers.CharField(source='description')
        freeDelivery = drf_serializers.SerializerMethodField()
        images = common_serializers.ImageSerializer(
            many=True, allow_null=True)
        reviews = ReviewSerializer(source='review_set', many=True)
        rating = drf_serializers.SerializerMethodField()

        def get_freeDelivery(self, obj: models.Product) -> bool:
            """
            Answers: Is it free for delivery?
            :param obj: Product
            :return: bool
            """
            return selectors.ProductSelector().is_free_delivery(obj)

        def get_rating(self, obj: models.Product) -> Optional[float]:
            """Rating for product from reviews."""
            avg_rating = selectors.ProductSelector().get_rating(obj.id)
            if avg_rating is not None:
                return round(avg_rating, 2)
            else:
                return None

    permission_classes = (permissions.AllowAny,)

    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Returns detailed information about Product.
        :param request:
        :return:
        """
        instance = get_object_or_404(models.Product, pk=kwargs.get('id'))
        serializer = self.OutputSerializer(
            instance=instance)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)


class ProductPopularApi(views.APIView):
    """Represents the best-selling products"""
    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """
        Represents the best-selling products witch are active
        :param request:
        :return:
        """
        selector = selectors.ProductSelector()
        products = selector.get_popular_products()
        output_serializer = serializers.ProductShortSerializer(
            instance=products, many=True)

        return drf_response.Response(
            data=output_serializer.data, status=status.HTTP_200_OK)


class ProductLimitedApi(views.APIView):
    """Represents products that are marked as limited"""
    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """
        Represents products that are marked as limited
        (and witch are active as well)
        :param request:
        :return:
        """
        selector = selectors.ProductSelector()
        products = selector.get_limited_products()
        output_serializer = serializers.ProductShortSerializer(
            instance=products, many=True)

        return drf_response.Response(
            data=output_serializer.data, status=status.HTTP_200_OK)
