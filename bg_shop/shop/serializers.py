from rest_framework import serializers
from shop import models, selectors
from common import serializers as common_serializers


class ProductShortSerializer(serializers.ModelSerializer):
    """"""
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
    date = serializers.DateField(source='release_date')
    description = serializers.CharField(source='short_description')
    freeDelivery = serializers.SerializerMethodField()
    images = common_serializers.ImageSerializer(
        many=True, allow_null=True)
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_freeDelivery(self, obj):
        return selectors.ProductSelector().is_free_delivery(obj)

    def get_reviews(self, obj):
        return selectors.ReviewSelector().count_reviews_for_product(obj.id)

    def get_rating(self, obj):
        avg_rating = selectors.ProductSelector().get_rating(obj.id)
        if avg_rating is not None:
            return round(avg_rating, 2)
        else:
            return None