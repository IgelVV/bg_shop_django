"""Serializers representing Cart and used in different apis."""

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
    """
    Based on Product obj.

    Represents ProductShort schema
    (without nested review and specifications serializers).
    """

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

    def __init__(self, *args, **kwargs) -> None:
        """Get and save `boundary_of_free_delivery` and actual `date`."""
        super().__init__(*args, **kwargs)
        self.boundary_of_free_delivery = conf_selectors \
            .AdminConfigSelector().boundary_of_free_delivery
        self.today = timezone.now().date()

    def get_price(self, obj: shop_models.Product) -> Decimal:
        """
        Get price of product taking into account discount.

        :param obj: Product.
        :return: discounted price.
        """
        discounted_price = shop_selectors.ProductSelector()\
            .get_discounted_price(
                product=obj,
                date=self.today,
        )
        return discounted_price

    def get_count(self, obj: shop_models.Product) -> int:
        """
        Get amount of Products that user added to cart.

        Product.quantity_ordered field must be annotated or added by other way.
        :param obj: Product.
        :return: number of Products in cart.
        """
        return obj.quantity_ordered

    def get_freeDelivery(self, obj: shop_models.Product) -> bool:
        """
        Calculate: Is delivery for this Product free.

        :param obj:
        :return:
        """
        if self.boundary_of_free_delivery:
            return obj.price >= self.boundary_of_free_delivery

    def get_reviews(self, obj: shop_models.Product) -> int:
        """
        Get amount of reviews about the Product.

        :param obj:
        :return:
        """
        if hasattr(obj, 'review_set'):
            return obj.review_set.count()

    def get_rating(self, obj: shop_models.Product) -> Optional[float]:
        """
        Calculate average rate of Product according reviews.

        :param obj: Product.
        :return: average rate, rounded to two decimal places
            or None, if there is no reviews.
        """
        if hasattr(obj, 'review_set'):
            avg_rating = obj.review_set \
                .aggregate(db_models.Avg('rate')).get("rate__avg", None)
            if avg_rating is not None:
                return round(avg_rating, 2)
            else:
                return None
