from typing import Optional

from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.db import models as db_models

from orders import models, services, selectors
from shop import models as shop_models
from common import serializers as common_serializers
from dynamic_config import selectors as conf_selectors


class CartApi(views.APIView):
    """
    If user is anonymous saves cart in sessions.

    If user is authenticated, saves cart in Order related with the user
    and that has an editing status, and adds session cart data in the order.
    """

    class InputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        count = serializers.IntegerField()

    class CartSerializer(serializers.ModelSerializer):
        """"""
        class Meta:
            model = shop_models.Product
            fields = (
                "id",
                "category",
                "price",
                "count",
                "date",
                "title",
                "description",
                "freeDelivery",
                "images",
                "tags",
                "reviews",
                "rating",
            )
            depth = 1

        category = serializers.IntegerField(source='category_id')
        count = serializers.SerializerMethodField()
        date = serializers.DateField(source='release_date')
        description = serializers.CharField(source='short_description')
        freeDelivery = serializers.SerializerMethodField()
        images = common_serializers.ImageSerializer(
            many=True, allow_null=True)
        reviews = serializers.SerializerMethodField()
        rating = serializers.SerializerMethodField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.boundary_of_free_delivery = conf_selectors\
                .AdminConfigSelector().boundary_of_free_delivery

        def get_count(self, obj) -> int:
            return obj.quantity_ordered

        def get_freeDelivery(self, obj) -> bool:
            if self.boundary_of_free_delivery:
                return obj.price >= self.boundary_of_free_delivery

        def get_reviews(self, obj) -> int:
            if hasattr(obj, 'review_set'):
                return obj.review_set.count()

        def get_rating(self, obj) -> Optional[float]:
            if hasattr(obj, 'review_set'):
                avg_rating = obj.review_set\
                    .aggregate(db_models.Avg('rate')).get("rate__avg", None)
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
        """Get items in basket"""
        selector = selectors.CartSelector(request=request)
        cart = selector.get_cart()
        output_serializer = self.CartSerializer(cart, many=True)
        response_data = output_serializer.data
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Add item to basket
        :param request:
        :param kwargs:
        :return:
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        service = services.CartService(request=request)
        service.add(
            product_id=validated_data.get("id"),
            quantity=validated_data.get("count"),
        )

        selector = selectors.CartSelector(request=request)
        cart = selector.get_cart()
        output_serializer = self.CartSerializer(cart, many=True)
        response_data = output_serializer.data
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)

    def delete(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Remove item from basket
        :param request:
        :param kwargs:
        :return:
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        service = services.CartService(request=request)
        service.remove(
            product_id=validated_data.get("id"),
            quantity=validated_data.get("count"),
        )

        selector = selectors.CartSelector(request=request)
        cart = selector.get_cart()
        output_serializer = self.CartSerializer(cart, many=True)
        response_data = output_serializer.data
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)
