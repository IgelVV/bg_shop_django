from typing import Any, Optional, Callable
from django.db import models as db_models
from django.utils import timezone

from shop import models, services


class SaleSelector:
    def get_sales(self, only_current: bool = True) -> db_models.QuerySet:
        sales = models.Sale.objects.all()\
            .select_related('product')\
            .prefetch_related("product__images")
        if only_current:
            now = timezone.now()
            sales = sales.filter(date_from__lte=now.date())\
                .filter(date_to__gte=now.date())
        return sales
