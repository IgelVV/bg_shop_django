from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from orders import models, services
from common import serializers as common_serializers


class CartApi(views.APIView):
    """
    If user is anonymous saves cart in sessions.
    If user is authenticated, returns Order related with the user
    and that has an editing status, and adds session cart data in the order.
    """
    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
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
