"""To get data about Cart (basket) from anywhere."""

from typing import TypeVar

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models as db_models

from rest_framework import request as drf_request

from orders import models
from shop import models as shop_models

UserType = TypeVar('UserType', bound=AbstractUser)


class CartSelector:
    """Depending on User interacts with sessions or with db Order model."""

    def __init__(self, request: drf_request.Request) -> None:
        """
        Create cart in session.

        :param request:
        """
        self.request = request
        self.session = request.session
        cart = request.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def get_cart(self) -> list[shop_models.Product]:
        """
        Get user's cart from session (if anonymous) or from Order obj.

        Prefetches a lot of related objects for serializer.

        Annotates `quantity_ordered` for every product, if cart is Order.
        If it isn't adds field `quantity_ordered` to every Product in list,
        after that output must be passed to serializer directly without
        any other changes.
        :return:
        """
        user: UserType = self.request.user
        if user.is_anonymous:
            cart_products = shop_models.Product.objects\
                .filter(id__in=self.cart.keys())

        else:
            cart_products = shop_models.Product.objects\
                .filter(
                    orderedproduct__order__user=user,
                    orderedproduct__order__status=models.Order.Statuses.CART
                )\
                .annotate(
                    quantity_ordered=db_models.Subquery(
                        models.OrderedProduct.objects.filter(
                            product=db_models.OuterRef("pk"),
                            order__user=user,
                            order__status=models.Order.Statuses.CART
                        )
                        .values("count")
                    )
                )

        cart_products = cart_products.prefetch_related("tags")\
            .prefetch_related("images")\
            .prefetch_related("review_set")\
            .prefetch_related("orderedproduct_set")\
            .prefetch_related("sale_set")

        cart_products = list(cart_products)

        # looks like `annotate` but in is not the same
        if user.is_anonymous:
            for product in cart_products:
                product.quantity_ordered = self.cart[str(product.id)]

        return cart_products
