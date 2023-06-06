from typing import Any, TypeVar, Optional

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models as db_models

from rest_framework import request as drf_request

from orders import models
from shop import models as shop_models

UserType = TypeVar('UserType', bound=AbstractUser)


class CartSelector:
    """"""
    def get_cart(
            self,
            request: drf_request.Request,
    ) -> list[shop_models.Product]:
        user: UserType = request.user
        if user.is_anonymous:
            cart: dict = request.session.get(settings.CART_SESSION_ID)
            if not cart:
                cart = {}
            cart_products = shop_models.Product.objects\
                .filter(id__in=cart.keys())

        else:
            cart_products = shop_models.Product.objects\
                .filter(
                    orderedproduct__order__user=user,
                    orderedproduct__order__status=models.Order.Statuses.EDITING
                )\
                .annotate(quantity_ordered=db_models.Subquery(
                    models.OrderedProduct.objects.filter(
                        product=db_models.OuterRef("pk"),
                        order__user=user,
                        order__status=models.Order.Statuses.EDITING
                    )
                    .values("count")
                ))

        cart_products = cart_products.prefetch_related("tags")\
            .prefetch_related("images")\
            .prefetch_related("review_set")\
            .prefetch_related("orderedproduct_set")

        cart_products = list(cart_products)

        # to `annotate` but in is not the same
        if user.is_anonymous:
            for product in cart_products:
                product.quantity_ordered = cart[str(product.id)]

        return cart_products
