import django_filters

from django.db import models as db_models

from shop import models


class BaseProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains')
    minPrice = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte')
    maxPrice = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte')
    freeDelivery = django_filters.BooleanFilter(
        method="filter_free_delivery",)
    available = django_filters.BooleanFilter(
        method="filter_available_in_stock",)
    category = django_filters.NumberFilter(
        field_name='category', lookup_expr='exact')
    tags = django_filters.AllValuesMultipleFilter(method="filter_tags",)

    class Meta:
        model = models.Product
        fields = ()

    def filter_free_delivery(
            self, queryset, name, value: bool) -> db_models.QuerySet:
        if value:
            return queryset.filter(**{name: True})
        return queryset

    def filter_available_in_stock(
            self, queryset, name, value: bool) -> db_models.QuerySet:
        if value:
            return queryset.filter(**{
                "count__gt": 0,
            })
        return queryset

    def filter_tags(self, queryset, name, value) -> db_models.QuerySet:
        if value:
            return queryset.filter(**{
                "tags__in": value,
            })
        else:
            return queryset
