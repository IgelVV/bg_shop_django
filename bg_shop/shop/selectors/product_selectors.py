from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, QuerySet

from shop import models
from dynamic_config import selectors as conf_selectors

User = get_user_model()


class ProductSelector:
    def get_viewed_products(self, user: User) -> QuerySet:
        ...

    def get_rating(self, product_id: int) -> float:
        reviews = models.Review.objects\
            .filter(product_id=product_id)\
            .aggregate(Avg("rate"))
        return reviews["rate__avg"]

    def is_free_delivery(self, product: models.Product) -> bool:
        boundary = conf_selectors.AdminConfigSelector().get_config(
            "boundary_of_free_delivery")
        if boundary:
            return product.price >= boundary
        else:
            return False
