from typing import Optional

from django.contrib.auth import get_user_model
from django.db import models as db_models

from orders import models
from shop import models as product_models


class OrderService:
    # todo check before confirmation that products are available and active
    def confirm(self):
        ...

    def change_status(self, order: models.Order, status: str) -> bool:
        # only one `editing` order can exist
        ...

    def create_order(self, **attrs):
        new_order = models.Order()
        new_order = self._set_attributes(new_order, **attrs)
        new_order.full_clean()
        new_order.save()
        return new_order

    def _set_attributes(
            self, order: models.Order,
            **attrs) -> models.Order:
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

    def add_product_to_order(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            override_quantity: bool = False,
    ) -> None:
        ord_prod_service = OrderedProductService()
        ordered_product = ord_prod_service.get_ordered_product_from_order(
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


class OrderedProductService:
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
                ordered_product = ordered_products.get(product_id=product_id)
            except models.OrderedProduct.DoesNotExist:
                ordered_product = None

        return ordered_product
