from decimal import Decimal
from typing import Optional, TypeVar

from rest_framework import request as drf_request

from django.db import models as db_models
from django.contrib.auth.models import AbstractUser

from orders import models, selectors

UserType = TypeVar('UserType', bound=AbstractUser)


class OrderService:
    # todo check before confirmation that products are available and active
    def confirm(self):
        ...

    # def change_status(self, order: models.Order, status: str) -> models.Order:
    #     # only one `cart` order can exist
    #     if order.status == status:
    #         return order
    #     if status == models.Order.Statuses.CART:
    #         user_carts = order.user.order_set\
    #             .filter(status=models.Order.Statuses.CART).count()
    #         if user_carts:
    #             raise ValueError('User can have only one cart')
    #     else:
    #         order.status = status
    #     order.full_clean()
    #     order.save()
    #     return order


    def create_order(self, *, commit: bool = True, **attrs):
        new_order = models.Order()
        new_order = self._set_attributes(new_order, **attrs)
        if commit:
            new_order.full_clean()
            new_order.save()
        return new_order

    def _set_attributes(
            self, order: models.Order,
            **attrs,
    ) -> models.Order:
        """
        Set new attributes for Order obj. passed in arguments,
        if they are acceptable. Does not save the object.
        :param order: instance of Order to change
        :param attrs: attrs for Order to set
        :return: the same object
        """
        for name, value in attrs.items():
            if hasattr(models.Order, name):
                setattr(order, name, value)
            else:
                raise AttributeError(
                    f"'Order' object has no attribute '{name}'")
        return order

    def get_total_cost(self, order: models.Order) -> Decimal:
        total_cost = Decimal()
        for ordered_prod in order.orderedproduct_set.all():
            total_cost += ordered_prod.price * ordered_prod.count
        return total_cost

    def edit(
            self,
            order: Optional[models.Order],
            products: list[dict],
            commit: bool = True,
    ) -> models.Order:
        order.status = models.Order.Statuses.EDITING
        self.update_ordered_products(order=order, products=products)
        if commit:
            order.full_clean()
            order.save()
        return order

    def update_ordered_products(
            self,
            order: models.Order,
            products: list[dict],
    ) -> None:
        simple_products = self._simplify_products(products=products)
        ordered_products: db_models.QuerySet[models.OrderedProduct] = \
            order.orderedproduct_set.all()
        for ord_prod in ordered_products:
            if ord_prod.product_id not in simple_products:
                ord_prod.delete()
            else:
                ord_prod.count = simple_products.pop(ord_prod.product_id)
                ord_prod.full_clean()
                ord_prod.save()
        for product_id, count in simple_products.items():
            OrderedProductService().create_ordered_product(
                order=order, product_id=product_id, quantity=count)

    def _simplify_products(self, products: list[dict]) -> dict[int, int]:
        simple_products = {}
        for product in products:
            simple_products[product['id']] = product['count']
        return simple_products


class OrderedProductService:
    def create_ordered_product(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            commit:bool = True,
    ) -> None:
        ordered_product = models.OrderedProduct(
            order=order,
            product_id=product_id,
            count=quantity
        )
        if commit:
            ordered_product.full_clean()
            ordered_product.save()

    def add_item(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            override_quantity: bool = False,
    ) -> None:
        # todo redo, it hits db a lot. and use create_ord_prod()
        #  it is better to use orderedproduct obj directly.
        """
        Increase `count` of OrderedProduct of overrides it.
        :param order:
        :param product_id:
        :param quantity:
        :param override_quantity:
        :return:
        """
        if quantity < 0:
            OrderedProductService().reduce_or_delete(
                order=order,
                product_id=product_id,
                quantity=-quantity,
            )

        ord_prod_selector = selectors.OrderedProductSelector()
        ordered_product = ord_prod_selector.get_ordered_product_from_order(
            order=order,
            product_id=product_id,
        )
        if ordered_product:
            if override_quantity:
                ordered_product.count = quantity
            else:
                ordered_product.count += quantity
        else:
            ordered_product = models.OrderedProduct(
                order=order,
                product_id=product_id,
                count=quantity
            )
        ordered_product.full_clean()
        ordered_product.save()


    def reduce_or_delete(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            remove_all: bool = False,
    ) -> None:
        ord_prod_selector = selectors.OrderedProductSelector()
        ordered_product = ord_prod_selector.get_ordered_product_from_order(
            order=order,
            product_id=product_id,
        )
        if ordered_product:
            if remove_all:
                ordered_product.delete()
            else:
                if ordered_product.count > quantity:
                    ordered_product.count -= quantity
                    ordered_product.full_clean()
                    ordered_product.save()
                else:
                    ordered_product.delete()
        else:
            raise ValueError(f"{order} has no Product with id {product_id}")
