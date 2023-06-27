"""Reusable serializers representing Order."""

from decimal import Decimal

from rest_framework import serializers as drf_serializers

from orders import models, selectors
import orders.serializers.ordered_product_serializer \
    as ordered_product_serializer


class OrderOutputSerializer(drf_serializers.ModelSerializer):
    """
    For representing Order model with related objects.

    Following fields should be prefetched
        - orderedproduct_set
            - product (select_related)
                - images
                - review_set
                - sale_set
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
            "deliveryCost",
            "totalCost",
            "status",
            "paid",
            "paymentType",
            "city",
            "address",
            "comment",
            "products",
        )

    createdAt = drf_serializers.DateTimeField(source="created_at")
    fullName = drf_serializers.CharField(source="user.get_full_name")
    email = drf_serializers.EmailField(source="user.email")
    phone = drf_serializers.CharField(
        source="user.profile.phone_number", allow_null=True)
    deliveryType = drf_serializers.CharField(source="delivery_type")
    deliveryCost = drf_serializers.SerializerMethodField()
    totalCost = drf_serializers.SerializerMethodField()
    status = drf_serializers.CharField()
    paymentType = drf_serializers.CharField(source="payment_type")
    products = ordered_product_serializer.OrderedProductOutputSerializer(
        source="orderedproduct_set", many=True, allow_null=True)

    def get_totalCost(self, obj: models.Order) -> Decimal:
        """
        Get total cost of Order.

        Main cost + delivery cost.
        :param obj: Order.
        :return: total cost.
        """
        return selectors.OrderSelector().get_total_cost(order=obj)

    def get_deliveryCost(self, obj: models.Order) -> Decimal:
        """
        Get delivery cost.

        :param obj: Order.
        :return: delivery cost.
        """
        return selectors.OrderSelector().get_delivery_cost(order=obj)
