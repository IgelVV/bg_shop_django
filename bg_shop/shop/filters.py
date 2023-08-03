"""It is used for filtering query sets in services"""
import django_filters

from django.db import models as db_models

from shop import models
from dynamic_config import selectors as conf_selectors


class BaseProductFilter(django_filters.FilterSet):
    """
    Filters queryset of products with passed filters.
    It is necessary to annotate Product object with freeDelivery
    to use this filter.
    """
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
        """
        Works only if queryset (qs) is annotated with `freeDelivery`
        :param queryset: qs to filter
        :param name: `freeDelivery` - name of field that calls this method
        :param value: bool
        :return: filtered qs
        """
        if value:
            boundary = conf_selectors.DynamicConfigSelector() \
                .boundary_of_free_delivery
            if boundary:
                queryset = queryset.annotate(
                    freeDelivery=db_models.Case(
                        db_models.When(
                            price__gte=boundary,
                            then=db_models.Value(True),
                        ),
                        default=db_models.Value(False),
                        output_field=db_models.BooleanField()
                    )
                )
            else:
                queryset = queryset.annotate(
                    freeDelivery=db_models.Value(False))

            return queryset.filter(**{name: True})
        return queryset

    def filter_available_in_stock(
            self, queryset, name, value: bool) -> db_models.QuerySet:
        """
        Checks if amount(count) of Product is greater than 0, if value is True,
        if value is False, returns original queryset (qs).
        And filter inactive products.
        :param queryset: qs of Products
        :param name: doesn't meter
        :param value: bool
        :return: filtered qs
        """
        if value:
            return queryset.filter(**{
                "count__gt": 0,
                "is_active": True,
            })
        return queryset

    def filter_tags(self, queryset, name, value) -> db_models.QuerySet:
        """
        Returns Products which related with tags passed as a value.
        :param queryset: qs of Products
        :param name: doesn't meter
        :param value: iterable obj. of tag's ids or single tag's id to compare
        :return: filtered qs
        """
        if value:
            return queryset.filter(**{
                "tags__in": value,
            }).distinct()
        else:
            return queryset
