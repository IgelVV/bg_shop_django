from rest_framework import status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from shop import selectors
from shop import serializers as shop_serializers


class BannerApi(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        selector = selectors.ProductSelector()
        banners = selector.get_products_in_banners()
        output_serializer = shop_serializers.ProductShortSerializer(
            instance=banners, many=True)

        return drf_response.Response(
            data=output_serializer.data, status=status.HTTP_200_OK)
