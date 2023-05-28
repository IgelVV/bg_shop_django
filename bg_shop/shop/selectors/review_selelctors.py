from django.contrib.auth import get_user_model
from django.db.models import Avg, QuerySet

from shop import models

User = get_user_model()


class ReviewSelector:
    def get_reviews_for_product(self, product_id: int) -> QuerySet:
        return models.Review.objects.filter(product=product_id)


    def count_reviews_for_product(self, product_id: int) -> int:
        return models.Review.objects.filter(product_id=product_id).count()
