from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.urls import reverse

from payment import tasks


class PaymentApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        number = serializers.CharField(max_length=8)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        order_id = int(kwargs['id'])
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
