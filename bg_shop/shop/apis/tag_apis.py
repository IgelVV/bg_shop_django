from rest_framework import status, permissions, views
from rest_framework import serializers as drf_serializers
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from shop import selectors


class TagApi(views.APIView):
    class QueryParamsSerializer(drf_serializers.Serializer):
        category = drf_serializers.IntegerField(required=False)

    class OutputSerializer(drf_serializers.Serializer):
        id = drf_serializers.IntegerField()
        name = drf_serializers.CharField()

    permission_classes = (permissions.AllowAny,)

    def get(self, request: drf_request.Request) -> drf_response.Response:
        """

        :param request:
        :return:
        """
        selector = selectors.TagSelector()
        params_serializer = self.QueryParamsSerializer(
            data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.validated_data
        if params:
            tags = selector.get_category_tags(category_id=params["category"])
        else:
            tags = selector.get_tags()
        output_serializer = self.OutputSerializer(tags, many=True)
        return drf_response.Response(
            data=output_serializer.data, status=status.HTTP_200_OK)
