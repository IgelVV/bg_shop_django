from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models


class Order(models.Model):
    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    class DeliveryTypes(models.TextChoices):
        ORDINARY = "OR", _("ordinary")
        EXPRESS = "EX", _("express")

    class Statuses(models.TextChoices):
        CART = "CT", _("cart")
        EDITING = "ED", _("editing")
        ACCEPTED = "AC", _("accepted")
        REJECTED = "RJ", _("rejected")
        COMPLETED = "CO", _("completed")

    class PaymentTypes(models.TextChoices):
        ONLINE = "ON", _("online")
        CASH = "CA", _("cash")
        SOMEONE = "SO", _("someone")  # just for fake payment

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at"),
    )
    delivery_type = models.CharField(
        max_length=2,
        choices=DeliveryTypes.choices,
        default=DeliveryTypes.ORDINARY,
        verbose_name=_("delivery type")
    )
    status = models.CharField(
        max_length=2,
        choices=Statuses.choices,
        default=Statuses.EDITING,
        verbose_name=_("status"),
    )
    city = models.CharField(
        max_length=255,
        verbose_name=_("city"),
        null=True,
        blank=True,
    )
    address = models.TextField(
        max_length=1024,
        verbose_name=_("address"),
        null=True,
        blank=True,
    )
    comment = models.TextField(
        max_length=1024,
        verbose_name=_("comment"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this order should be treated as active. "
            "Unselect this instead of deleting orders."
        ),
    )
    paid = models.BooleanField(default=False, verbose_name=_("paid"))
    payment_type = models.CharField(
        max_length=2,
        choices=PaymentTypes.choices,
        default=PaymentTypes.ONLINE,
        verbose_name=_("payment_type"),
    )


class OrderedProduct(models.Model):
    class Meta:
        verbose_name = _("ordered product")
        verbose_name_plural = _("ordered products")
        unique_together = ("product", "order",)

    product = models.ForeignKey(
        "shop.Product",
        on_delete=models.PROTECT,
        verbose_name=_("product"),
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        verbose_name=_("order"),
    )
    # In a moment of confirmation order
    price = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("price"),
    )
    count = models.SmallIntegerField(
        validators=[MinValueValidator(0)],
        default=1,
        verbose_name=_("count")
    )
