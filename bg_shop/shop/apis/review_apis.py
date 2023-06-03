from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from shop import models, selectors, services
from common import serializers as common_serializers


class ReviewApi(views.APIView):

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        response_data = [
            {
                "author": "Annoying Orange",
                "email": "no-reply@mail.ru",
                "text": "rewrewrwerewrwerwerewrwerwer",
                "rate": 4,
                "date": "2023-05-05 12:12"
            }
        ]
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)
