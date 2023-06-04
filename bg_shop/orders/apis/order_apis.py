from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from orders import models, services
from common import serializers as common_serializers


class OrdersApi(views.APIView):
    def get(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """Get all (active) orders as history"""
        response_data =[
            {
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
        ]
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)

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
        response_data ={
            "orderId": 123
        }
        return drf_response.Response(
            data=response_data, status=status.HTTP_200_OK)


class OrderDetailApi(views.APIView):
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
        response_data ={
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
        """
        Confirm order. Url args: <int: id> -Order id.
        Request body: Order
        :param request:
        :param kwargs:
        :return:
        """
        if True:
            return drf_response.Response(status=status.HTTP_200_OK)
