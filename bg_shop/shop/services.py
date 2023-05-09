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


class OrderService:
    def change_status(self, order: models.Order, status: str) -> bool:
        ...


class CartService:
    def add_product_to_cart(
            self, user: User, product: 'models.Product', count: int) -> None:
        ...


class ReviewService:
    def add_review(
            self,
            user: User,
            product: 'models.Product',
            text: str,
            rate: float
    ) -> tuple['models.Review', bool]:
        ...


class SaleService:
    def create_sale(self):
        ...
