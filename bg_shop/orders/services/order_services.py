"""Business logic related to Order."""

from typing import Optional, TypeVar, Any

from django.db import models as db_models
from django.db import transaction
from django.contrib.auth.models import AbstractUser

from orders import models, selectors

import orders.services.ordered_product_services as ord_prod_services

UserType = TypeVar('UserType', bound=AbstractUser)


class OrderService:
    """Business logic related to Order."""

    def create_order(self, *, commit: bool = True, **attrs) -> models.Order:
        """
        Create new Order with passed attributes.

        :param commit: if True, full_clean() and save()
        :param attrs: fields with values to set in new Order.
        :return: created Order.
        """
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
        Set attributes for Order obj.

        Set values for Order's fields passed in arguments,
        if they are acceptable.
        Does not save the object.
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

    def edit(
            self,
            order: models.Order,
            order_attrs: Optional[dict] = None,
            products: Optional[list[dict]] = None,
            commit: bool = True,
    ) -> models.Order:
        """
        Edit Order.

        Changes order status to `EDITING`, and updates passed params of order.
        order_attrs_example = {
            "delivery_type": "EX",
            "city": "Moscow",
            "address": "red square 1",
            "comment": "",
        }
        :param order: Order obj.
        :param order_attrs: {field: value,}
        :param products: list of dictionary with information about product
        (from serializer).
        :param commit: If True, full_clean(), save().
        :return: Order (with status = Editing).
        """
        order.status = models.Order.Statuses.EDITING
        if order_attrs:
            order = self._set_attributes(order=order, **order_attrs)
        if products:
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
        """
        Update OrderedProducts related to the Order.

        After this method OrderedProduct and `products` will match each other.
        :param order: Order obj.
        :param products: information about Products related to OrderedProducts
            (main info is: id, count)
        :return: None
        """
        ordered_product_service = ord_prod_services.OrderedProductService()
        simple_products = self._simplify_products(products=products)
        ordered_products: db_models.QuerySet[models.OrderedProduct] = \
            order.orderedproduct_set.all().select_related("product") \
            .prefetch_related("product__sale_set")
        for ord_prod in ordered_products:
            if ord_prod.product_id not in simple_products:
                ord_prod.delete()
            else:
                ordered_product_service.update_price(ord_prod, commit=False)
                ord_prod.count = simple_products.pop(ord_prod.product_id)
                ord_prod.full_clean()
                ord_prod.save()
        for product_id, count in simple_products.items():
            ordered_product_service.create_ordered_product(
                order=order, product_id=product_id, quantity=count)

    def _simplify_products(self, products: list[dict]) -> dict[int, int]:
        """
        Parse important information.

        :param products: info about product in order.
        :return: important product info.
        """
        simple_products = {}
        for product in products:
            simple_products[product['id']] = product['count']
        return simple_products

    def confirm(
            self,
            order_id: int,
            user: UserType,
            order_data: dict,
    ) -> None:
        """
        Confirm Order.

        Updates Order data, deduct product items, update price of
        ordered products, and sets Order.status = ACCEPTED.
        :param order_id: Order.pk
        :param user: User obj.
        :param order_data: {field: value,}
        :return: None
        """
        # todo with transaction atomic
        selector = selectors.OrderSelector()
        ordered_product_service = ord_prod_services.OrderedProductService()

        order = selector.get_editing_order_of_user(
            order_id=order_id, user=user, or_404=True)
        order_attrs = self._parse_order_data(order_data=order_data)
        order = self.edit(order=order, order_attrs=order_attrs, commit=False)

        ordered_products = order.orderedproduct_set.all()
        ordered_product_service.deduct_amount_from_product(
            ord_prod_qs=ordered_products)
        for ord_prod in ordered_products:
            ordered_product_service.update_price(
                ordered_product=ord_prod, commit=True)

        order.status = order.Statuses.ACCEPTED
        order.full_clean()
        order.save()

    def _parse_order_data(self, order_data: dict) -> dict:
        """
        Parse only important info for Order.

        :param order_data: All info from input serializer.
        :return: important info {field: value}
        """
        order_attrs: dict[str, Any | None] = dict()

        order_attrs["delivery_type"] = order_data.get("deliveryType")
        order_attrs["payment_type"] = order_data.get("paymentType")
        order_attrs["city"] = order_data.get("city", None)
        order_attrs["address"] = order_data["address"]
        order_attrs["comment"] = order_data.get("comment", None)
        return order_attrs

    def reject(
            self,
            order_id: int,
    ) -> None:
        """
        Reject Order.

        If payment operation is not successful.
        Roll back deduction of products that were reserved
        when order was confirmed.
        :param order_id:
        :return:
        """
        order = models.Order.objects.get(pk=order_id)

        with transaction.atomic():
            order.status = models.Order.Statuses.REJECTED
            ord_prod_service = ord_prod_services.OrderedProductService()
            ord_prod_service.return_ordered_products(
                ord_prod_qs=order.orderedproduct_set.all()
            )
            order.full_clean()
            order.save()
