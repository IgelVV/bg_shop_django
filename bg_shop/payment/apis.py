"""API Views for fake payment system."""

from rest_framework import serializers, status, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.urls import reverse

from payment import tasks
from orders import selectors as order_selectors


class PaymentApi(views.APIView):
    """Fake payment system."""

    class InputSerializer(serializers.Serializer):
        """Handle fake card number."""

        number = serializers.CharField(max_length=8)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """Start payment with passed `card number`."""
        order_id = int(kwargs['id'])
        check = order_selectors.OrderSelector().check_if_order_belongs_to_user(
            user=request.user,
            order_id=order_id
        )
        if not check:
            return drf_response.Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        tasks.third_party_payment_service.delay(
            url=request.build_absolute_uri(
                reverse("api:payment:payment-webhook")),
            order_id=order_id,
            card_number=validated_data["number"],
            payment=1,
        )
        return drf_response.Response(status=status.HTTP_200_OK)
