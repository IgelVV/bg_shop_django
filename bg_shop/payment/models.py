from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Payment(models.Model):
    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        verbose_name=_("order"),
    )
    number = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99999999)],
        verbose_name=_("number")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )
    validity_period = models.DateField(verbose_name=_("validity period"))
    code = models.IntegerField(verbose_name=_("code"))
    payment_type = models.ForeignKey(
        "PaymentType",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("payment type")
    )


class PaymentType(models.Model):
    class Meta:
        verbose_name = _("payment type")
        verbose_name_plural = _("payment types")

    class TypeChoices(models.TextChoices):
        ONLINE = "ON", _("online")
        RANDOM = "RN", _("random")

    name = models.CharField(
        max_length=2,
        choices=TypeChoices.choices,
        verbose_name=_("name"),
    )
