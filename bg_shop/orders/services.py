from django.contrib.auth import get_user_model

from orders import models
from shop import models as product_models

User = get_user_model()


class OrderService:
    def change_status(self, order: models.Order, status: str) -> bool:
        ...


class CartService:
    def add_product_to_cart(
            self, user: User,
            product: product_models.Product,
            count: int) -> None:
        ...
