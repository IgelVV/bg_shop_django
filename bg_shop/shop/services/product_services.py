from typing import Optional

from shop import models


class ProductService:
    def deduct_items(self, product_id: int, amount: int) -> None:
        # the same as in OrderedProductService().deduct_amount_from_product()
        # product = models.Product.objects.select_for_update().get(pk=product_id)
        ...
