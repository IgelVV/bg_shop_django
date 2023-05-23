import django_filters

from shop import models


class BaseProductFilter(django_filters.FilterSet):
    ...
#     class Meta:
#         model = models.Product
#         fields = ("id", "email", "is_admin")
