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


# filling cart >
# orders/ POST - creating order from cart >
# filling order >
# orders/id/ POST - confirmation > ...

# existed order >
# orders/id/ Get - to edit order (if EDITING) >
# editing >
# orders/id/ POST - confirmation > ...

# new order from api without using cart >
# orders/ POST - create order with passed data >
# if cart exists, fill it with passed data, if not create new order ED
class OrdersApi(views.APIView):
    class InputSerializer(drf_serializers.Serializer):
        """Short Product"""
        class ImageSerializer(drf_serializers.Serializer):
            src = drf_serializers.CharField()
            alt = drf_serializers.CharField(
                max_length=255,
                required=False,
                allow_null=True,
                allow_blank=True
            )

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
        orderId = drf_serializers.IntegerField(source="pk")

    permission_classes = (permissions.IsAuthenticated,)

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
        Create new order. request body - basket[ordered product].
        It does not really create new Order, if cart exists,
        but changes status of existing Order that is used as cart,
        and updates data about products.
        :param request:
        :param kwargs:
        :return:
        """
        input_serializer = self.InputSerializer(data=request.data, many=True)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        selector = selectors.OrderSelector()
        cart_order = selector.get_or_create_cart_order(user=request.user)

        service = services.OrderService()
        order = service.edit(order=cart_order, products=validated_data)

        response_data = self.PostOutputSerializer(order).data
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
        selector = selectors.OrderSelector()
        order = selector.get_order_of_user(
            order_id=kwargs.get('id'), user=request.user)
        if order:
            serializer = serializers.OrderSerializer(order)
            return drf_response.Response(
                data=serializer.data, status=status.HTTP_200_OK)
        else:
            return drf_response.Response(status=status.HTTP_404_NOT_FOUND)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        # todo change frontend history: if order ED - redirect
        #  to creating order

        # todo check that order status was cart or editing,
        #  if editing - different behaviour
        """
        Confirm order. Url args: <int: id> -Order id.
        Request body: Order
        :param request:
        :param kwargs:
        :return:
        """
        if True:
            return drf_response.Response(status=status.HTTP_200_OK)
