from typing import Optional

from django.db import models as db_models

from orders import models


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
            ordered_products = models.OrderedProduct.objects \
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