from typing import TypeVar, Optional

from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models as db_models

from rest_framework import request as drf_request

from orders import models, services, selectors
from shop import models as product_models


UserType = TypeVar('UserType', bound=AbstractUser)


class OrderSelector:
    def get_or_create_cart_order(
            self,
            user: UserType,
            prefetch_ordered_products: bool = True,
    ) -> models.Order:
        order = self.get_cart_order(
            user=user, prefetch_ordered_products=prefetch_ordered_products)
        if order:
            return order
        else:
            order = services.OrderService().create_order(
                user=user, status=models.Order.Statuses.CART)
        return order

    def get_cart_order(
            self,
            user: UserType,
            prefetch_ordered_products: bool = True
    ) -> Optional[models.Order]:
        """
        :param user:
        :param prefetch_ordered_products:
        :return:
        """
        qs = models.Order.objects.filter(
            user_id=user.pk,
            status=models.Order.Statuses.CART,
        )
        if prefetch_ordered_products:
            qs = qs.prefetch_related("orderedproduct_set")
        if qs.count():  # todo if more than 1...
            order = qs[0]
        else:
            order = None
        return order

    def get_order_history(
            self,
            user: UserType,
    ) -> db_models.QuerySet[models.Order]:
        """

        :param user:
        :return:
        """
        ordered_products_prefetch_qs = models.OrderedProduct.objects\
            .select_related('product')\
            .prefetch_related("product__images")\
            .prefetch_related("product__review_set")

        orders = models.Order.objects\
            .filter(user=user)\
            .filter(is_active=True)\
            .exclude(status=models.Order.Statuses.CART)\
            .prefetch_related(
                db_models.Prefetch(
                    'orderedproduct_set',
                    queryset=ordered_products_prefetch_qs
                )
            ).select_related("user__profile")
        return orders

    def get_order_of_user(
            self,
            order_id: int,
            user: UserType,
    ) -> Optional[models.Order]:
        """
        return ony if this order related with the user
        :param order_id:
        :param user:
        :return:
        """
        orders = self.get_order_history(user=user)
        try:
            order = orders.get(pk=order_id)
        except models.Order.DoesNotExist:
            order = None
        return order


class OrderedProductSelector:
    def get_ordered_product_from_order(
            self,
            *,
            order: Optional[models.Order] = None,
            order_id: Optional[int] = None,
            product_id: int,
    ) -> Optional[models.OrderedProduct]:
        """

        :param order:
        :param order_id:
        :param product_id:
        :return:
        """
        if (order and order_id) or not (order or order_id):
            raise ValueError(
                f"Only one of args ('oder' or 'order_id') can be passed, "
                f"but it is passed: {order=}, {order_id=}."
            )
        if order:
            ordered_products: db_models.QuerySet[models.OrderedProduct] = \
                order.orderedproduct_set.all()
        else:
            ordered_products = models.OrderedProduct.objects\
                .filter(order_id=order_id)
        ordered_product: Optional[models.OrderedProduct] = None
        if ordered_products:
            try:
                # todo it hits db even if ordered prod were prefetched
                ordered_product = ordered_products.get(product_id=product_id)
                # ordered_product = ordered_products[0] it does not hit db
            except models.OrderedProduct.DoesNotExist:
                ordered_product = None

        return ordered_product
