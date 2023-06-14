from decimal import Decimal
from typing import Optional

from django.db import models as db_models
from django.utils import timezone

from rest_framework import serializers

from common import serializers as common_serializers
from shop import models as shop_models
from shop import selectors as shop_selectors
from dynamic_config import selectors as conf_selectors


class CartSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = shop_models.Product
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

    category = serializers.IntegerField(source='category_id')
    price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    date = serializers.DateField(source='release_date')
    description = serializers.CharField(source='short_description')
    freeDelivery = serializers.SerializerMethodField()
    images = common_serializers.ImageSerializer(
        many=True, allow_null=True)
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boundary_of_free_delivery = conf_selectors \
            .AdminConfigSelector().boundary_of_free_delivery
        self.today = timezone.now().date()

    def get_price(self, obj) -> Decimal:
        discounted_price = shop_selectors.ProductSelector()\
            .get_discounted_price(
                product=obj,
                date=self.today
            )
        return discounted_price

    def get_count(self, obj) -> int:
        return obj.quantity_ordered

    def get_freeDelivery(self, obj) -> bool:
        if self.boundary_of_free_delivery:
            return obj.price >= self.boundary_of_free_delivery

    def get_reviews(self, obj) -> int:
        if hasattr(obj, 'review_set'):
            return obj.review_set.count()

    def get_rating(self, obj) -> Optional[float]:
        if hasattr(obj, 'review_set'):
            avg_rating = obj.review_set \
                .aggregate(db_models.Avg('rate')).get("rate__avg", None)
            if avg_rating is not None:
                return round(avg_rating, 2)
            else:
                return None
