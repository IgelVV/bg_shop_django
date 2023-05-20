from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from orders import models, services
from common import serializers as common_serializers


class OrderDetailApi(views.APIView):
    ...
