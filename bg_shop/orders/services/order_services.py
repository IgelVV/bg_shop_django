from decimal import Decimal

from orders import models, selectors


class OrderService:
    # todo check before confirmation that products are available and active
    def confirm(self):
        ...

    def change_status(self, order: models.Order, status: str) -> bool:
        # only one `cart` order can exist
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

    def get_total_cost(self, order: models.Order) -> Decimal:
        total_cost = Decimal()
        for ordered_prod in order.orderedproduct_set.all():
            total_cost += ordered_prod.price * ordered_prod.count
        return total_cost


class OrderedProductService:
    def add_item(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            override_quantity: bool = False,
    ) -> None:
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
