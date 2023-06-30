"""
Api Views related to Orders.

Except of Orders that used as Cart.
"""

from rest_framework import status, permissions, views
from rest_framework import serializers as drf_serializers
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from orders import services, serializers, selectors, tasks
from account import validators as acc_validators


class OrdersApi(views.APIView):
    """
    Not for specific orders.

    GET: order history.
    POST: create new order.
    """

    class PostOutputSerializer(drf_serializers.Serializer):
        """Info about created order."""

        orderId = drf_serializers.IntegerField(source="pk")

    permission_classes = (permissions.IsAuthenticated,)

    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Order History of user.

        Get all (active, not status.CART) orders of user as a history.
        :param request:
        :param kwargs:
        :return:
        """
        selector = selectors.OrderSelector()
        orders = selector.get_order_history(user=request.user)
        serializer = serializers.OrderOutputSerializer(orders, many=True)
        return drf_response.Response(
            data=serializer.data, status=status.HTTP_200_OK)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        # todo orderedproducts must contain actual prices after this method
        #  it displayed on order-detail page
        """
        Create new order.

        Contains ordered products information only
        (request body - basket[ordered product]).
        It does not really create new Order, if cart exists,
        but changes status of existing Order that is used as cart,
        and updates data about products.

        It is necessary to confirm order after creating, and add order info
        (e.g. delivery_address)
        :param request:
        :param kwargs:
        :return:
        """
        input_serializer = serializers.OrderedProductInputSerializer(
            data=request.data, many=True)
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
    """
    Interaction with a specific order.

    GET: info about order.
    POST: confirm order.
    """

    class InputSerializer(drf_serializers.Serializer):
        """
        Order data with detail ordered_product data.

        Order[OrderedProduct].
        """

        id = drf_serializers.IntegerField()
        createdAt = drf_serializers.DateTimeField()
        fullName = drf_serializers.CharField(max_length=300)
        email = drf_serializers.EmailField()
        phone = drf_serializers.CharField(
            validators=[acc_validators.PhoneRegexValidator()])
        deliveryType = drf_serializers.CharField()
        paymentType = drf_serializers.CharField()  # todo choice
        totalCost = drf_serializers.DecimalField(
            max_digits=8, decimal_places=2,)
        status = drf_serializers.CharField()
        city = drf_serializers.CharField()
        address = drf_serializers.CharField()
        comment = drf_serializers.CharField(allow_null=True, allow_blank=True)
        products = serializers.OrderedProductInputSerializer(
            many=True, required=False)

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InputSerializer

    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Get order.

        User can request only his orders (or 404).
        Url args: <int: id> - Order id.
        :param request:
        :param kwargs:
        :return:
        """
        selector = selectors.OrderSelector()
        order = selector.get_one_order_of_user(
            order_id=kwargs.get('id'), user=request.user)
        if order:
            serializer = serializers.OrderOutputSerializer(order)
            return drf_response.Response(
                data=serializer.data, status=status.HTTP_200_OK)
        else:
            return drf_response.Response(status=status.HTTP_404_NOT_FOUND)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Confirm order.

        Order to confirm must already exist and have EDITING status.
        Invokes task.
        Url args: <int: id> - Order id.
        Request body: Order[OrderedProduct]
        :param request:
        :param kwargs:
        :return:
        """
        order_id = kwargs.get('id')
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        service = services.OrderService()
        service.confirm(
            order_id=order_id, user=request.user, order_data=validated_data)

        tasks.order_confirmed.delay(order_id)

        return drf_response.Response(
            data=validated_data, status=status.HTTP_200_OK)
