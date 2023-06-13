from typing import TypeVar, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models as db_models
from django.http import Http404

from orders import models, services
from orders import filters as order_filters

UserType = TypeVar('UserType', bound=AbstractUser)


class OrderSelector:
    def get_orders(
            self,
            *,
            filters: Optional[dict] = None,
    ) -> db_models.QuerySet[models.Order]:
        orders = models.Order.objects.all()
        if filters:
            orders = order_filters.BaseOrderFilter(
                data=filters, queryset=orders).qs
        return orders

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
        order = qs.first()

        return order

    def get_orders_of_user(
            self,
            user: UserType,
    ) -> db_models.QuerySet[models.Order]:
        orders = models.Order.objects \
            .filter(user=user) \
            .filter(is_active=True)
        return orders

    def get_order_history(
            self,
            user: UserType,
    ) -> db_models.QuerySet[models.Order]:
        """

        :param user:
        :return:
        """
        orders = self.get_orders_of_user(user=user)
        orders = orders.exclude(status=models.Order.Statuses.CART)
        orders = self._prefetch_data(
            orders_qs=orders,
            with_user_profile=True,
            with_images_and_reviews=True
        )
        return orders

    def _prefetch_data(
            self,
            orders_qs: db_models.QuerySet[models.Order],
            with_images_and_reviews: bool = False,
            with_user_profile: bool = False,
    ) -> db_models.QuerySet[models.Order]:
        """
        Does prefetch_related for 'orderedproduct_set'
        and 'product' related with them.
        Optionally, also prefetches 'images', 'review_set' related with product
        and 'user' and 'profile' related with Order.
        :param orders_qs:
        :param with_images_and_reviews:
        :param with_user_profile:
        :return:
        """
        ordered_products_prefetch_qs = models.OrderedProduct.objects \
            .select_related('product')
        if with_images_and_reviews:
            ordered_products_prefetch_qs = ordered_products_prefetch_qs \
                .prefetch_related("product__images") \
                .prefetch_related("product__review_set")

        orders_qs = orders_qs \
            .prefetch_related(
            db_models.Prefetch(
                'orderedproduct_set',
                queryset=ordered_products_prefetch_qs
            )
        )
        if with_user_profile:
            orders_qs = orders_qs.select_related("user__profile")
        return orders_qs

    def get_order_of_user(
            self,
            order_id: int,
            user: UserType,
            exclude_cart: bool = True,
    ) -> Optional[models.Order]:
        """
        return ony if this order related with the user
        :param order_id:
        :param user:
        :param exclude_cart:
        :return:
        """
        orders = self.get_orders_of_user(user=user)
        if exclude_cart:
            orders = orders.exclude(status=models.Order.Statuses.CART)
        orders = self._prefetch_data(
            orders_qs=orders,
            with_user_profile=True,
            with_images_and_reviews=True,
        )
        try:
            order = orders.get(pk=order_id)
        except models.Order.DoesNotExist:
            order = None
        return order

    def get_editing_order_of_user(
            self,
            order_id: int,
            user: UserType,
            or_404: bool = True,
    ) -> Optional[models.Order]:
        orders = self.get_orders_of_user(user=user)
        orders = orders.filter(status=models.Order.Statuses.EDITING)
        orders = self._prefetch_data(orders_qs=orders)
        try:
            order = orders.get(pk=order_id)
        except models.Order.DoesNotExist:
            if or_404:
                raise Http404(
                    f"Order (id={order_id}) related with {user} doesn't "
                    f"have status EDITING or doesn't exist."
                )
            else:
                order = None
        return order


