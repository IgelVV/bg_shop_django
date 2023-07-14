"""Reusable serializers representing OrderedProduct."""

from typing import Optional

from django.db import models as db_models

from rest_framework import serializers as drf_serializers

from common import serializers as common_serializers
from orders import models
from dynamic_config import selectors as conf_selectors


class OrderedProductOutputSerializer(drf_serializers.ModelSerializer):
    """
    For representing OrderedProduct model with related objects.

    Looks like Cart serializer, but uses OrderedProduct model
    instead of Product.

    Following fields should be prefetched:
        - product (select_related)
        - images
        - review_set
        - sale_set
    """

    class TagSerializer(drf_serializers.Serializer):
        """Represents Tag model."""

        id = drf_serializers.IntegerField()
        name = drf_serializers.CharField()

    class Meta:
        model = models.OrderedProduct
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )
        depth = 1

    id = drf_serializers.IntegerField(source='product.pk')
    category = drf_serializers.IntegerField(source='product.category_id')
    date = drf_serializers.DateField(source='product.release_date')
    title = drf_serializers.CharField(source='product.title')
    description = drf_serializers.CharField(source='product.short_description')
    freeDelivery = drf_serializers.SerializerMethodField()
    images = common_serializers.ImageSerializer(
        source='product.images', many=True, allow_null=True)
    tags = TagSerializer(
        source='product.tags', many=True, allow_null=True)
    reviews = drf_serializers.SerializerMethodField()
    rating = drf_serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs) -> None:
        """Get and save `boundary_of_free_delivery`."""
        super().__init__(*args, **kwargs)
        self.boundary_of_free_delivery = conf_selectors \
            .DynamicConfigSelector().boundary_of_free_delivery

    def get_freeDelivery(self, obj: models.OrderedProduct) -> bool:
        """
        Calculate: Is delivery for this OrderedProduct free.

        :param obj:
        :return:
        """
        if self.boundary_of_free_delivery:
            return obj.price >= self.boundary_of_free_delivery

    def get_reviews(self, obj: models.OrderedProduct) -> int:
        """
        Get amount of reviews about the OrderedProduct.product.

        :param obj:
        :return:
        """
        if hasattr(obj.product, 'review_set'):
            return obj.product.review_set.count()

    def get_rating(self, obj: models.OrderedProduct) -> Optional[float]:
        """
        Calculate average rate of OrderedProduct.product according reviews.

        :param obj: OrderedProduct.
        :return: average rate, rounded to two decimal places
            or None, if there is no reviews.
        """
        if hasattr(obj.product, 'review_set'):
            avg_rating = obj.product.review_set \
                .aggregate(db_models.Avg('rate')).get("rate__avg", None)
            if avg_rating is not None:
                return round(avg_rating, 2)
            else:
                return None


class OrderedProductInputSerializer(drf_serializers.Serializer):
    """ProductShort schema."""

    class ImageSerializer(drf_serializers.Serializer):
        """Represents Image."""

        src = drf_serializers.CharField()
        alt = drf_serializers.CharField(
            max_length=255,
            required=False,
            allow_null=True,
            allow_blank=True
        )

    class TagSerializer(drf_serializers.Serializer):
        """Represents Tag."""

        id = drf_serializers.IntegerField()
        name = drf_serializers.CharField()

    id = drf_serializers.IntegerField()
    category = drf_serializers.IntegerField(required=False, allow_null=True,)
    price = drf_serializers.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        required=False,
    )
    count = drf_serializers.IntegerField()
    date = drf_serializers.DateTimeField()
    title = drf_serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    description = drf_serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    freeDelivery = drf_serializers.BooleanField(
        required=False, allow_null=True)
    images = common_serializers.ImageSerializer(
        many=True,
        required=False,
        allow_null=True,
    )
    tags = TagSerializer(many=True, required=False, allow_null=True)
    reviews = drf_serializers.IntegerField(required=False, allow_null=True)
    rating = drf_serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
