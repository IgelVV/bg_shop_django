from typing import Any
from django.contrib.auth import get_user_model

from common import models


User = get_user_model()


class AdminConfigService:
    def get_config(self, key: str) -> Any:
        ...


class ImageService:
    @staticmethod
    def get_img_url(image: models.Image) -> str:
        url: str = image.img.url
        return url
