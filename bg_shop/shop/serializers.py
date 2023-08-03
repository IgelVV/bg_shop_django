from decimal import Decimal
from typing import Optional

from django.utils import timezone
from django.db import models as db_models

from rest_framework import serializers
from shop import models, selectors
from common import serializers as common_serializers
from dynamic_config import selectors as conf_selectors


class ProductShortSerializer(serializers.ModelSerializer):
    """Represents Product obj for displaying on cards. Product obj must
    be annotated with additional fields: date, freeDelivery, rating."""
    class Meta:
        model = models.Product
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
            .DynamicConfigSelector().boundary_of_free_delivery
        self.today = timezone.now().date()

    def get_price(self, obj) -> Decimal:
        discounted_price = selectors.ProductSelector()\
            .get_discounted_price(
                product=obj,
                date=self.today
            )
        return discounted_price

    def get_freeDelivery(self, obj) -> bool:
        if self.boundary_of_free_delivery:
            return obj.price >= self.boundary_of_free_delivery
        else:
            return False

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
