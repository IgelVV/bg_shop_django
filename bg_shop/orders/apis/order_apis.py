from rest_framework import status, permissions, views
from rest_framework import serializers as drf_serializers
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.db import models as db_models
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from orders import models, services, serializers, selectors
from common import serializers as common_serializers


User = get_user_model()


class OrdersApi(views.APIView):
    class InputSerializer(drf_serializers.Serializer):
        class TagSerializer(drf_serializers.Serializer):
            id = drf_serializers.IntegerField()
            name = drf_serializers.CharField()

        id = drf_serializers.IntegerField()
        category = drf_serializers.IntegerField()
        price = drf_serializers.DecimalField(
            default=0,
            max_digits=8,
            decimal_places=2,
        )
        count = drf_serializers.IntegerField()
        date = drf_serializers.DateTimeField()
        title = drf_serializers.CharField()
        description = drf_serializers.CharField()
        freeDelivery = drf_serializers.BooleanField(required=False, )
        images = common_serializers.ImageSerializer(
            many=True,
            required=False,
            allow_null=True,
        )
        tags = TagSerializer(many=True, required=False, )
        reviews = drf_serializers.IntegerField()
        rating = drf_serializers.DecimalField(
            max_digits=8,
            decimal_places=2,
            required=False,
            allow_null=True,
        )

    class PostOutputSerializer(drf_serializers.Serializer):
        orderId = drf_serializers.IntegerField()

    permission_classes = (permissions.IsAuthenticated,)

    # todo manage permissions
    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """Get all (active, not CART status) orders of user as history"""

        selector = selectors.OrderSelector()
        orders = selector.get_order_history(user=request.user)
        serializer = serializers.OrderSerializer(orders, many=True)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)


    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Create new order. request body - basket[ordered product]
        :param request:
        :param kwargs:
        :return:
        """
        if not request.user.is_anonymous:
            response_data = {
                "orderId": 0
            }
        else:
            response_data = {
                "orderId": 0
            }
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)


class OrderDetailApi(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # todo user can get only his orders
    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Get order. Url args: <int: id> -Order id.
        :param request:
        :param kwargs:
        :return:
        """
        response_data = {
            "id": 123,
            "createdAt": "2023-05-05 12:12",
            "fullName": "Annoying Orange",
            "email": "no-reply@mail.ru",
            "phone": "88002000600",
            "deliveryType": "free",
            "paymentType": "online",
            "totalCost": 567.8,
            "status": "accepted",
            "city": "Moscow",
            "address": "red square 1",
            "products": [
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
        }
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        # todo check that order status was cart (or editing)
        """
        Confirm order. Url args: <int: id> -Order id.
        Request body: Order
        :param request:
        :param kwargs:
        :return:
        """
        if True:
            return drf_response.Response(status=status.HTTP_200_OK)
