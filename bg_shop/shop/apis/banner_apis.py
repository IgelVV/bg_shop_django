from rest_framework import status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from api import utils as api_utils
from api import pagination
from shop import models, selectors, services
from shop import serializers as shop_serializers


class BannerApi(views.APIView):
    def get(self, request: drf_request.Request) -> drf_response.Response:
        data = [
            {
                "id": 123,
                "category": 2,
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
            data=data, status=status.HTTP_200_OK)
