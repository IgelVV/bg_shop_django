from rest_framework import serializers
from common import models


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    alt = serializers.CharField(source="description", max_length=255)

    def get_src(self, obj):
        if obj.img:
            return obj.img.url
        else:
            return None

    class Meta:
        model = models.Image
        fields = ("src", "alt",)
