from django.db import models as db_models

from shop import models


class BannerSelector:
    def get_banners(self) -> db_models.QuerySet:
        """
        To get all banner with cached related products.
        :return: all banners
        """
        return models.Banner.objects.all().select_related('product')
