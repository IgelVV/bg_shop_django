from django.db import models as db_models
from django.db import transaction

from orders import models, selectors
from shop import models as shop_models
from shop import selectors as shop_selectors


class OrderedProductService:
    def create_ordered_product(
            self,
            order: models.Order,
            product_id: int,
            quantity: int,
            commit: bool = True,
    ) -> None:
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
            raise ValueError(f"{order} has no Product with id {product_id}")

    def update_price(
            self,
            ordered_product: models.OrderedProduct,
            commit: bool = True
    ) -> None:
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
        :param ord_prod_qs:
        :return:
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
