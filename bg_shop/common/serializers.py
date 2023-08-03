from typing import Optional

from rest_framework import serializers
from common import models, services


class ImageSerializer(serializers.ModelSerializer):
    """To reuse in other ModelSerializers"""
    src = serializers.SerializerMethodField()
    alt = serializers.CharField(source="description", max_length=255)

    def get_src(self, obj: models.Image) -> Optional[str]:
        """Returns image source ulr or None"""
        if obj.img:
            url = services.ImageService().get_img_url(obj)
            return url
        else:
            return None

    class Meta:
        model = models.Image
        fields = ("src", "alt",)
