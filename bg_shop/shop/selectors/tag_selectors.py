from django.db import models as db_models

from shop import models


class TagSelector:
    def get_category_tags(self, category_id: int) -> db_models.QuerySet:
        tags = models.Tag.objects.filter(product__category=category_id).distinct()
        return tags

    def get_tags(self) -> db_models.QuerySet:
        return models.Tag.objects.all()
