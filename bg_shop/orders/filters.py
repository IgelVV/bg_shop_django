"""Filters for querysets."""

import django_filters

from orders import models


class BaseOrderFilter(django_filters.FilterSet):
    """Filters queryset of orders with passed filters."""
    class Meta:
        model = models.Order
        fields = ("user", "status", "is_active")
