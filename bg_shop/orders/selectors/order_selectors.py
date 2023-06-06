from typing import TypeVar

from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from rest_framework import request as drf_request

from orders import models, services, selectors
from shop import models as product_models


UserType = TypeVar('UserType', bound=AbstractUser)


class OrderSelector:
    def get_current_order(
            self,
            user: UserType,
            prefetch_ordered_products: bool = True
    ) -> models.Order:
        qs = models.Order.objects.filter(
            user_id=user.pk,
            status=models.Order.Statuses.EDITING,
        )
        if prefetch_ordered_products:
            qs = qs.prefetch_related("orderedproduct_set")
        if qs.count():  # todo if more than 1...
            order = qs[0]
        else:
            order = services.OrderService().create_order(
                user=user, status=models.Order.Statuses.EDITING)
        return order
