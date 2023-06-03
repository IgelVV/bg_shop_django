# from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class DynamicConfig(models.Model):
    """Singleton"""
    class Meta:
        verbose_name = _("dynamic config")
        verbose_name_plural = _("dynamic configs")

    id = models.IntegerField(primary_key=True, default=1)

    regular_delivery_cost = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0), ],
        verbose_name=_("regular delivery cost"),
        help_text=_(
            "sets base cost of delivery"),
    )  # 200
    express_delivery_extra_charge = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0), ],
        verbose_name=_("express delivery extra charge"),
    )  # 500
    boundary_of_free_delivery = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0), ],
        verbose_name=_("boundary of free delivery"),
    )  # 2000
    company_info = models.TextField(
        max_length=5120,
        null=True,
        blank=True,
        verbose_name=_("company info")
    )
    legal_address = models.TextField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name=_("legal address")
    )
    main_phone = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name=_("main phone")
    )
    main_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("main email")
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    # @classmethod
    # def load(cls):
    #     obj, created = cls.objects.get_or_create(pk=1)
    #     return obj

    def __str__(self):
        return f'{_("Dynamic config")}'
