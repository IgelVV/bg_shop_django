from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from payment import models


class PaymentApi(views.APIView):

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:

        return drf_response.Response(status=status.HTTP_200_OK)
