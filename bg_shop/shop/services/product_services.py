from django.contrib.auth import get_user_model

from shop import models

User = get_user_model()


class ProductService:
    def get_viewed_products(self, user: User) -> models.Product:
        ...

    # to selectors??
    def get_rating(self, product: models.Product) -> float:
        ...

    def is_free_delivery(self, product: models.Product) -> bool:
        ...
