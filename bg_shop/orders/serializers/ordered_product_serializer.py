from typing import Optional

from django.db import models as db_models

from rest_framework import serializers as drf_serializers

from common import serializers as common_serializers
from orders import models
from dynamic_config import selectors as conf_selectors


class OrderedProductSerializer(drf_serializers.ModelSerializer):
    """
    Following fields should be prefetched....
    """

    class TagSerializer(drf_serializers.Serializer):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boundary_of_free_delivery = conf_selectors \
            .AdminConfigSelector().boundary_of_free_delivery

    def get_freeDelivery(self, obj) -> bool:
        if self.boundary_of_free_delivery:
            return obj.price >= self.boundary_of_free_delivery

    def get_reviews(self, obj) -> int:
        if hasattr(obj.product, 'review_set'):
            return obj.product.review_set.count()

    def get_rating(self, obj) -> Optional[float]:
        if hasattr(obj.product, 'review_set'):
            avg_rating = obj.product.review_set \
                .aggregate(db_models.Avg('rate')).get("rate__avg", None)
            if avg_rating is not None:
                return round(avg_rating, 2)
            else:
                return None
