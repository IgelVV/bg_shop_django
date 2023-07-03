"""To get data about Orders."""

from decimal import Decimal
from typing import TypeVar, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models as db_models
from django import http

from orders import models, services
from orders import filters as order_filters
from dynamic_config import selectors as dynamic_selectors

UserType = TypeVar('UserType', bound=AbstractUser)


class OrderSelector:
    """Contains methods for getting information about Orders."""

    def get_orders(
            self,
            *,
            filters: Optional[dict] = None,
    ) -> db_models.QuerySet[models.Order]:
        """
        Get Order queryset.

        :param filters: dict of filter conditions (e.g. {user_id: 1,})
        :return: queryset of Orders.
        """
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
        """
        Get or create Order related to user, with status=CART.

        :param user: User object.
        :param prefetch_ordered_products: if True prefetches
            related ordered products.
        :return: Order.
        """
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
        Get Order related to user, with status=CART.

        :param user: User object.
        :param prefetch_ordered_products: if True prefetches
            related ordered products.
        :return: Order.
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
            exclude_cart: bool = True,
    ) -> db_models.QuerySet[models.Order]:
        """
        Get all active Orders related to user.

        :param user: User object.
        :param exclude_cart: if True, excludes Orders with CART statuses.
        :return: queryset of Orders.
        """
        orders = models.Order.objects \
            .filter(user=user) \
            .filter(is_active=True)
        if exclude_cart:
            orders = orders.exclude(status=models.Order.Statuses.CART)
        return orders

    def get_order_history(
            self,
            user: UserType,
            order_by_date: bool = True,
    ) -> db_models.QuerySet[models.Order]:
        """
        Get all active Orders related to user for api response.

        Prefetches related objects.
        :param user: User obj.
        :param order_by_date: if True, sorts Orders by created_at descending.
        :return: queryset of Orders (prefetched: orderedproduct_set',
            'product', 'sale_set', 'images', 'review_set', 'user', 'profile'.).
        """
        orders = self.get_orders_of_user(user=user)
        if order_by_date:
            orders = orders.order_by('-created_at')
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
        Prefetch related data.

        Does prefetch_related for 'orderedproduct_set'
        and 'product' related with them, also 'sale_set' of each product.
        Optionally, also prefetches 'images', 'review_set' related with product
        and 'user' and 'profile' related with Order.
        :param orders_qs: queryset of Orders
        :param with_images_and_reviews: if True, prefetches 'product__images'
            and 'product__review_set'.
        :param with_user_profile: if True, deos select_related 'user__profile'.
        :return: queryset of Orders (prefetched: orderedproduct_set',
            'product', 'sale_set', 'images', 'review_set', 'user', 'profile'.).
        """
        ordered_products_prefetch_qs = models.OrderedProduct.objects \
            .select_related('product') \
            .prefetch_related("product__sale_set")
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

    def get_one_order_of_user(
            self,
            order_id: int,
            user: UserType,
    ) -> Optional[models.Order]:
        """
        Get Order by id only if this order related with the user.

        Prefetches related objects.
        :param order_id: pk.
        :param user: User obj.
        :return: Order (prefetched: orderedproduct_set',
            'product', 'sale_set', 'images', 'review_set', 'user', 'profile'.)
            or None (if not found).
        """
        orders = self.get_orders_of_user(user=user)
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
        """
        Get Order with status EDITING and related to user.

        :param order_id: pk.
        :param user: User obj.
        :param or_404: if True, raise Http404 when the Order not found.
        :return: Order (prefetched: orderedproduct_set',
            'product', 'sale_set'.)
            or None (if not found).
        """
        orders = self.get_orders_of_user(user=user)
        orders = orders.filter(status=models.Order.Statuses.EDITING)
        orders = self._prefetch_data(orders_qs=orders)
        try:
            order = orders.get(pk=order_id)
        except models.Order.DoesNotExist:
            if or_404:
                raise http.Http404(
                    f"Order (id={order_id}) related with {user} doesn't "
                    f"have status EDITING or doesn't exist."
                )
            else:
                order = None
        return order

    def get_total_cost(self, order: models.Order) -> Decimal:
        """
        Calculate total cost of Order.

        Main total cost - cost of all ordered products (
            taking into account discounts),
        Delivery cost - depends on DynamicConfig.
        :param order: Order.
        :return: price of entire order.
        """
        main_cost = self.get_order_main_cost(order=order)
        is_express = order.delivery_type == models.Order.DeliveryTypes.EXPRESS
        delivery_cost = self.get_delivery_cost(
            main_cost=main_cost,
            is_express=is_express
        )
        total_cost = main_cost + delivery_cost
        return total_cost

    def get_order_main_cost(self, order: models.Order) -> Decimal:
        """
        Calculate cost of ordered products.

        Taking into account discounts.
        :param order: Order.
        :return: sum of all prices of ordered items.
        """
        cost = Decimal()
        for ordered_prod in order.orderedproduct_set.all():
            cost += ordered_prod.price * ordered_prod.count
        return cost

    def get_delivery_cost(
            self,
            main_cost: Optional[Decimal] = None,
            is_express: Optional[bool] = None,
            order: Optional[models.Order] = None,
    ) -> Decimal:
        """
        Calculate delivery cost.

        `main_cost` and `is_express` should be passed or `order` instead.
        :param main_cost: should be passed with `is_express`,
            if `order` is None.
        :param is_express: should be passed with `main_cost`,
            if `order` is None.
        :param order: Order obj.
            If `order` arg is passed, finds other args values from passed obj.
        :return: cost of delivery.
        """
        if order and ((is_express is not None) or (main_cost is not None)):
            raise AttributeError("It's prohibited to pass `order` "
                                 "with alter args")
        elif (order is None) and (
                (is_express is None) or (main_cost is None)):
            raise AttributeError(
                "If 'order' arg is not passed, "
                "both 'is_express' and 'main_cost' args are required."
            )
        if order:
            is_express = (
                order.delivery_type == models.Order.DeliveryTypes.EXPRESS
            )
            main_cost = self.get_order_main_cost(order=order)
        conf_selector = dynamic_selectors.AdminConfigSelector()
        delivery_cost = Decimal(0)
        if main_cost < conf_selector.boundary_of_free_delivery:
            delivery_cost += conf_selector.ordinary_delivery_cost
        if is_express:
            delivery_cost += conf_selector.express_delivery_extra_charge
        return delivery_cost
