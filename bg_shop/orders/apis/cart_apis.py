from rest_framework import status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request
from rest_framework import serializers as drf_serializers

from orders import services, selectors, serializers


class CartApi(views.APIView):
    """
    If user is anonymous saves cart in sessions.

    If user is authenticated, saves cart in Order related with the user
    and that has an editing status, and adds session cart data in the order.
    """

    class InputSerializer(drf_serializers.Serializer):
        id = drf_serializers.IntegerField()
        count = drf_serializers.IntegerField()

    permission_classes = (permissions.AllowAny,)

    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """Get items in basket"""
        selector = selectors.CartSelector(request=request)
        cart = selector.get_cart()
        output_serializer = serializers.CartSerializer(cart, many=True)
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
        output_serializer = serializers.CartSerializer(cart, many=True)
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
        output_serializer = serializers.CartSerializer(cart, many=True)
        response_data = output_serializer.data
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)
