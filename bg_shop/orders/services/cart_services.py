from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import request as drf_request


from orders import models
from shop import models as product_models

User = get_user_model()


class CartService:
    # def __init__(self, request: drf_request.Request) -> None:
    #     self.session = request.session
    #     cart = request.session.get(settings.CART_SESSION_ID)
    #     if not cart:
    #         cart = self.session[settings.CART_SESSION_ID] = {}
    #     self.cart = cart

    # def add(self, product, quantity=1, override_quantity=False):
    #     product_id = str(product.id)
    #     if product_id not in self.cart:
    #         self.cart[product_id] = {'quantity': 0,
    #                                  'price': str(product.price)}
    #     if override_quantity:
    #         self.cart[product_id]['quantity'] = quantity
    #     else:
    #         self.cart[product_id]['quantity'] += quantity
    #     self.save()
    #
    # def save(self):
    #     self.session.modified = True
    #
    # def remove(self, product):
    #     product_id = str(product.id)
    #     if product_id in self.cart:
    #         del self.cart[product_id]
    #         self.save()


    def add_product_to_cart(
            self, user: User,
            product: product_models.Product,
            count: int) -> None:
        ...
