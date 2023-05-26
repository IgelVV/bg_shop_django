from typing import Any, Optional, Callable
from django.db import models as db_models

from shop import models, services


class BannerSelector:
    def get_banners(self) -> db_models.QuerySet:
        return models.Banner.objects.all().select_related('product')
