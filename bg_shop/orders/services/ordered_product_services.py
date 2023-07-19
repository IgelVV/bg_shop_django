"""Business logic related to OrderedProduct."""

from django.db import models as db_models
from django.db import transaction

from orders import models, selectors
from shop import models as shop_models
from shop import selectors as shop_selectors


class OrderedProductService:
    """Business logic related to OrderedProduct."""

    def create_ordered_product(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            commit: bool = True,
    ) -> None:
        """
        Create new OrderedProduct.

        New OrderedProduct has actual price.
        :param order: Order obj.
        :param product_id: Product.pk
        :param quantity: amount of Product items.
        :param commit: if True, full_clean() and save().
        :return: None.
        """
        ordered_product = models.OrderedProduct(
            order=order,
            product_id=product_id,
            count=quantity
        )
        self.update_price(ordered_product=ordered_product, commit=False)
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
        Increase `count` of OrderedProduct or overrides it.

        Saves OrderedProduct.
        :param order: Order obj.
        :param product_id: Product.pk.
        :param quantity: `count`
        :param override_quantity: if True, sets quantity, instead of adding.
        :return: None.
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
        """
        Decrease OrderedProduct.count if possible.

        If `quantity` > OrderedProduct.count, deletes OrderedProduct.
        :param order: Order obj.
        :param product_id: Product.pk,
            if Product is not related to the OrderedProduct raises ValueError.
        :param quantity: amount to deduct.
        :param remove_all: if True, deletes OrderedProduct.
        :return: None.
        """
        # todo redo, it hits db a lot. and use create_ord_prod()
        #  it is better to use orderedproduct obj directly.
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
            raise models.OrderedProduct.DoesNotExist(
                f"{order} has no Product with id {product_id}")

    def update_price(
            self,
            ordered_product: models.OrderedProduct,
            commit: bool = True
    ) -> None:
        """
        Refresh OrderedProduct.price.

        Uses related Product.price taking into account discount.
        :param ordered_product: OrderedProduct obj.
        :param commit: If True, full_clean(), save().
        :return: None.
        """
        product_selector = shop_selectors.ProductSelector()
        ordered_product.price = product_selector.get_discounted_price(
            product=ordered_product.product)
        if commit:
            ordered_product.full_clean()
            ordered_product.save()

    def deduct_amount_from_product(
            self,
            ord_prod_qs: db_models.QuerySet[models.OrderedProduct],
    ) -> None:
        """
        Decrease related Product.count by OrderedProduct.count.

        If Product.count is not enough or Product.is_active=False,
        raises ValueError.
        :param ord_prod_qs: queryset of OrderedProduct.
        :return: None.
        """
        ord_prod_qs.select_related("product").select_for_update(of=("product"))
        with transaction.atomic():
            for ord_prod in ord_prod_qs:
                product: shop_models.Product = ord_prod.product
                if product.count < ord_prod.count:
                    raise ValueError(
                        f"Product({product.pk}).count is less then "
                        f"OrderedProduct({ord_prod.pk}).count")
                elif not product.is_active:
                    raise ValueError(f"Product({product.pk}) is not active")
                else:
                    product.count -= ord_prod.count
                    product.save()

    def return_ordered_products(
            self,
            ord_prod_qs: db_models.QuerySet[models.OrderedProduct],
    ) -> None:
        """
        Increase Product.count by OrderedProduct.count.

        To roll back previous deducting.
        :param ord_prod_qs: queryset of OrderedProduct.
        :return: None.
        """
        ord_prod_qs.select_related("product").select_for_update(of=("product"))
        with transaction.atomic():
            for ord_prod in ord_prod_qs:
                product: shop_models.Product = ord_prod.product
                product.count += ord_prod.count
                product.save()
