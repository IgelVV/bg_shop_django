from django.contrib.auth import get_user_model

from common import models


class ImageService:
    @staticmethod
    def get_img_url(image: models.Image) -> str:
        url: str = image.img.url
        return url
