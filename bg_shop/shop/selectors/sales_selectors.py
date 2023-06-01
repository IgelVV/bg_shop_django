from django.db import models as db_models
from django.utils import timezone

from shop import models


class SaleSelector:
    def get_sales(self, only_current: bool = True) -> db_models.QuerySet:
        """
        :param only_current: If True, returns Sales that starts before now
        and ends after now, if False returns all Sales
        :return: queryset of sales with cached products and images
        """
        sales = models.Sale.objects.all()\
            .select_related('product')\
            .prefetch_related("product__images")
        if only_current:
            now = timezone.now()
            sales = sales.filter(date_from__lte=now.date())\
                .filter(date_to__gte=now.date())
        return sales
