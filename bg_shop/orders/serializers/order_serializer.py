from decimal import Decimal
from typing import Optional, Union

from django.db import models as db_models

from rest_framework import serializers as drf_serializers

from orders import models, services
import orders.serializers.ordered_product_serializer \
    as ordered_product_serializer


# ._state.fields_cache
# ._prefetched_objects_cache
class OrderSerializer(drf_serializers.ModelSerializer):
    """
    Following fields should be prefetched
        - orderedproduct_set
            - product (select_related)
                - images
                - review_set
        - user (select_related)
            - profile (select_related)
    (e.g qs_orders.prefetch_related(
        Prefetch('orderedproduct_set', queryset=OrderedProduct.objects
        .select_related('product').prefetch_related("images"))
    """
    class Meta:
        model = models.Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    createdAt = drf_serializers.DateTimeField(source="created_at")
    fullName = drf_serializers.CharField(source="user.get_full_name")
    email = drf_serializers.EmailField(source="user.email")
    phone = drf_serializers.IntegerField(source="user.profile.phone_number")
    deliveryType = drf_serializers.CharField(
        source="get_delivery_type_display")
    totalCost = drf_serializers.SerializerMethodField()
    status = drf_serializers.CharField(source="get_status_display")
    products = ordered_product_serializer.OrderedProductSerializer(
        source="orderedproduct_set", many=True, allow_null=True)

    def get_totalCost(self, obj: models.Order) -> Decimal:
        return services.OrderService().get_total_cost(obj)
