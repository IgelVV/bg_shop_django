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
    freeDelivery = serializers.BooleanField()
    images = common_serializers.ImageSerializer(
        many=True, allow_null=True)
    reviews = serializers.IntegerField()
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        avg_rating = obj.rating
        if avg_rating is not None:
            return round(avg_rating, 2)
        else:
            return None
