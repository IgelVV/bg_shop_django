from django.utils.translation import gettext_lazy as _
from django.db import models

from payment import validators


class Payment(models.Model):
    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    class Services(models.TextChoices):
        TEST = "TE", _("test")

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        verbose_name=_("order"),
    )
    service = models.CharField(
        max_length=2,
        choices=Services.choices,
        default=Services.TEST,
        verbose_name=_("service")
    )
    payment_id = models.CharField(max_length=255, verbose_name=_("payment id"))
