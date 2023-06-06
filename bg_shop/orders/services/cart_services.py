from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import request as drf_request

from orders import models, services, selectors
from shop import models as product_models

User = get_user_model()


class CartService:
    def __init__(self, request: drf_request.Request) -> None:
        self.request = request
        self.session = request.session
        cart = request.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id: int, quantity: int = 1, override_quantity=False):
        if self.request.user.is_anonymous:
            self._add_to_session(product_id, quantity, override_quantity)
        else:
            self._add_to_order(product_id, quantity, override_quantity)

    def _add_to_session(
            self,
            product_id: int,
            quantity: int = 1,
            override_quantity: bool = False,
    ) -> None:
        product_id_key = str(product_id)
        if product_id_key not in self.cart:
            self.cart[product_id_key] = 0
        if override_quantity:
            self.cart[product_id_key] = quantity
        else:
            self.cart[product_id_key] += quantity
        self.save_session()

    def save_session(self):
        self.session.modified = True

    def _add_to_order(
            self,
            product_id: int,
            quantity: int = 1,
            override_quantity=False
    ) -> None:
        current_order = selectors.OrderSelector()\
            .get_current_order(user=self.request.user)
        order_service = services.OrderService()
        order_service.add_product_to_order(
            order=current_order,
            product_id=product_id,
            quantity=quantity,
            override_quantity=override_quantity
        )

    # def remove(self, product):
    #     product_id = str(product.id)
    #     if product_id in self.cart:
    #         del self.cart[product_id]
    #         self.save()

