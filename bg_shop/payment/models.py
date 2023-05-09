from django.utils.translation import gettext_lazy as _
from django.db import models

from payment import validators


class Payment(models.Model):
    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    class TypeChoices(models.TextChoices):
        ONLINE = "ON", _("online")
        RANDOM = "RN", _("random")

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        verbose_name=_("order"),
    )
    number = models.CharField(
        max_length=8,
        validators=[validators.PaymentNumberRegexValidator],
        verbose_name=_("number")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )
    validity_period = models.DateField(verbose_name=_("validity period"))
    code = models.IntegerField(verbose_name=_("code"))
    payment_type = models.CharField(
        max_length=2,
        choices=TypeChoices.choices,
        verbose_name=_("payment type"),
    )
