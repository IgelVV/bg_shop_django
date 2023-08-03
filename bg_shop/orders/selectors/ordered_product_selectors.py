"""To get data related to OrderedProduct."""

from typing import Optional

from django.db import models as db_models

from orders import models


class OrderedProductSelector:
    """To get data related to OrderedProduct."""

    def get_ordered_product_from_order(
            self,
            *,
            order: Optional[models.Order] = None,
            order_id: Optional[int] = None,
            product_id: int,
    ) -> Optional[models.OrderedProduct]:
        """
        Get OrderedProduct related to the Product and the Order.

        It allowed to pass or `order`, or `order_id` not both.
        :param order: Order obj.
        :param order_id: pk of Order obj.
        :param product_id: pk of Product.
        :return: OrderedProduct obj
            or None.
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
            ordered_products = models.OrderedProduct.objects \
                .filter(order_id=order_id)
        ordered_product: Optional[models.OrderedProduct] = None
        try:
            for ord_product in ordered_products:
                if ord_product.product_id == product_id:
                    ordered_product = ord_product
                    break
        except models.OrderedProduct.DoesNotExist:
            ordered_product = None
        return ordered_product
