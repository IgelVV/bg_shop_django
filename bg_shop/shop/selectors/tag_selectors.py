from django.db import models as db_models

from shop import models


class TagSelector:
    def get_category_tags(self, category_id: int) -> db_models.QuerySet:
        """Returns all tags related to all products that related
        to passed category"""
        return (models.Tag.objects
                .filter(product__category=category_id).distinct())

    def get_tags(self) -> db_models.QuerySet:
        """Returns all existing tags."""
        return models.Tag.objects.all()
