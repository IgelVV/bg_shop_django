from django.contrib.auth import get_user_model
from django.db.models import Avg, QuerySet

from shop import models

User = get_user_model()


class ReviewSelector:
    def get_reviews_for_product(self, product_id: int) -> QuerySet:
        """Product related Reviews"""
        return models.Review.objects.filter(product=product_id)


    def count_reviews_for_product(self, product_id: int) -> int:
        """Amount of reviews for product"""
        return models.Review.objects.filter(product_id=product_id).count()
