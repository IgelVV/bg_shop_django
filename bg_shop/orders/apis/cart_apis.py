from typing import Optional

from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.db import models as db_models
from django.shortcuts import get_object_or_404

from orders import models, services, selectors
from shop import models as shop_models
from common import serializers as common_serializers
from dynamic_config import selectors as conf_selectors


class CartApi(views.APIView):
    """
    If user is anonymous saves cart in sessions.
    If user is authenticated, returns Order related with the user
    and that has an editing status, and adds session cart data in the order.
    """

    class InputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        count = serializers.IntegerField()

    class CartSerializer(serializers.ModelSerializer):
        """"""
        # todo
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
        reviews = serializers.IntegerField()
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
                avg_rating = obj.review_set.aggregate(db_models.Avg('rate'))
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
        selector = selectors.CartSelector()
        service = services.CartService()
        request.session['cart'] = {'1': 5, '3': 2}
        # del request.session['cart']
        request.session.modified = True
        cart = selector.get_cart(request=request)
        output_serializer = self.CartSerializer(cart, many=True)
        response_data = output_serializer.data

        response_data = [
            {
                "id": 123,
                "category": 55,
                "price": 500.67,
                "count": 11,
                "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                "title": "video card",
                "description": "description of the product",
                "freeDelivery": True,
                "images": [
                    {
                        "src": "/3.png",
                        "alt": "Image alt string"
                    }
                ],
                "tags": [
                    {
                        "id": 12,
                        "name": "Gaming"
                    }
                ],
                "reviews": 5,
                "rating": 4.6
            }
        ]
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
        response_data = [
            {
                "id": 123,
                "category": 55,
                "price": 500.67,
                "count": 12,
                "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                "title": "video card",
                "description": "description of the product",
                "freeDelivery": True,
                "images": [
                    {
                        "src": "/3.png",
                        "alt": "Image alt string"
                    }
                ],
                "tags": [
                    {
                        "id": 12,
                        "name": "Gaming"
                    }
                ],
                "reviews": 5,
                "rating": 4.6
            }
        ]
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
        response_data = [
            {
                "id": 123,
                "category": 55,
                "price": 500.67,
                "count": 10,
                "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                "title": "video card",
                "description": "description of the product",
                "freeDelivery": True,
                "images": [
                    {
                        "src": "/3.png",
                        "alt": "Image alt string"
                    }
                ],
                "tags": [
                    {
                        "id": 12,
                        "name": "Gaming"
                    }
                ],
                "reviews": 5,
                "rating": 4.6
            }
        ]
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)
