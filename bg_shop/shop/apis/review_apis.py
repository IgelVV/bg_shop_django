from rest_framework import serializers, status, permissions, views
from rest_framework import response as drf_response
from rest_framework import request as drf_request

from django.core.validators import MinValueValidator

from shop import models, selectors, services


class ReviewApi(views.APIView):
    """For adding reviews for products."""

    class InputSerializer(serializers.Serializer):
        # todo rebuild. Hire is a lot of fields that are unnecessary
        """"""
        author = serializers.CharField(
            max_length=300,
            required=False,
            allow_null=True,
            allow_blank=True
        )  # useless (from current user)
        email = serializers.EmailField(
            required=False,
            allow_null=True,
            allow_blank=True,
        )  #useless (from current user)
        text = serializers.CharField(
            max_length=1024, allow_null=True, allow_blank=True, required=False)
        rate = serializers.IntegerField(
            validators=[MinValueValidator(0)],)
        date = serializers.DateTimeField(required=False, allow_null=True)  # useless (auto now)

    class OutputSerializer(serializers.ModelSerializer):
        """The same structure as in ProductDetailApi"""
        class Meta:
            model = models.Review
            fields = (
                "author",
                "email",
                "text",
                "rate",
                "date",
            )

        author = serializers.CharField(source="author.username")
        email = serializers.EmailField(source="author.email")

    permission_classes = (permissions.IsAuthenticated,)

    def post(
            self,
            request: drf_request.Request,
            **kwargs
    ) -> drf_response.Response:
        """
        Creates a new review related with product. Author is current user.
        :param request: contains data for creating review
        :param kwargs: contains id of product
        :return: response
        """
        product_id = kwargs["id"]
        author = request.user

        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        service = services.ReviewService()
        service.create_review(
            user_id=author.id,
            product_id=product_id,
            text=validated_data.get("text", None),
            rate=validated_data.get("rate"),
        )

        selector = selectors.ReviewSelector()
        reviews = selector.get_reviews_for_product(product_id=product_id)
        output_serializer = self.OutputSerializer(reviews, many=True)
        return drf_response.Response(
            data=output_serializer.data, status=status.HTTP_200_OK)
