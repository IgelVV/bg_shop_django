"""Business logic related to Cart (Order.status = Cart, or session.cart)."""

from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import request as drf_request

from orders import models, services, selectors

User = get_user_model()


class CartService:
    """Business logic related to Cart."""

    def __init__(self, request: drf_request.Request) -> None:
        """Save request and session for further use."""
        self.request = request
        self.session = request.session
        cart = request.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def save_session(self) -> None:
        """Cause session saving."""
        self.session.modified = True

    def add(
            self,
            product_id: int,
            quantity: int = 1,
            override_quantity: bool = False,
    ) -> None:
        """
        Add Product to Cart.

        Depending on User auth, uses session or Order obj.
        :param product_id: Product.pk
        :param quantity: amount of items to add
        :param override_quantity: If True, replace previous quantity by new one
        :return:
        """
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
        """
        Add product to cart stored in session.

        :param product_id: Product.pk
        :param quantity: amount of items to add
        :param override_quantity: If True, replace previous quantity by new one
        :return:
        """
        product_id_key = str(product_id)
        if product_id_key not in self.cart:
            self.cart[product_id_key] = 0
        if override_quantity:
            self.cart[product_id_key] = quantity
        else:
            self.cart[product_id_key] += quantity
        self.save_session()

    def _add_to_order(
            self,
            product_id: int,
            quantity: int = 1,
            override_quantity: bool = False,
    ) -> None:
        """
        Add product to cart stored in Order.

        :param product_id: Product.pk
        :param quantity: amount of items to add
        :param override_quantity: If True, replace previous quantity by new one
        :return:
        """
        cart_order: models.Order = selectors.OrderSelector() \
            .get_or_create_cart_order(user=self.request.user)
        service = services.OrderedProductService()
        service.add_item(
            order=cart_order,
            product_id=product_id,
            quantity=quantity,
            override_quantity=override_quantity
        )

    def remove(self, product_id: int, quantity: int = 1) -> None:
        """
        Subtract items from cart.

        :param product_id: Product.pk
        :param quantity: amount to subtract.
        :return: None
        """
        if self.request.user.is_anonymous:
            self._remove_from_session(product_id, quantity)
        else:
            self._remove_from_order(product_id, quantity)

    def _remove_from_session(
            self,
            product_id: int,
            quantity: int = 1,
    ) -> None:
        """
        Subtract items from cart stored in session.

        :param product_id: Product.pk
        :param quantity: amount to subtract.
        :return: None
        """
        product_id_key = str(product_id)
        if product_id_key in self.cart:
            self.cart[product_id_key] -= quantity
            if self.cart[product_id_key] <= 0:
                del self.cart[product_id_key]
        self.save_session()

    def _remove_from_order(
            self,
            product_id: int,
            quantity: int = 1,
    ) -> None:
        """
        Subtract items from cart stored in Order.

        :param product_id: Product.pk
        :param quantity: amount to subtract.
        :return: None
        """
        cart_order = selectors.OrderSelector() \
            .get_or_create_cart_order(user=self.request.user)
        ord_prod_service = services.OrderedProductService()
        ord_prod_service.reduce_or_delete(
            order=cart_order,
            product_id=product_id,
            quantity=quantity,
        )

    def merge_carts(self, session_cart: dict[str, int]) -> None:
        """
        Transfers cart items from session to Order.

        It is used for saving cart when user is logging in.
        :param session_cart: dict{'product_id': quantity: int,}
            to merge with users cart stored into Order
        :return: None
        """
        for product_id, quantity in session_cart.items():
            product_id = int(product_id)
            self._add_to_order(
                product_id=product_id,
                quantity=quantity,
                override_quantity=True,
            )
