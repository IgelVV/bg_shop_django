from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from account import validators


class Profile(models.Model):
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    phone_number = models.CharField(
        validators=[
            validators.PhoneRegexValidator(
                message=_("Phone number must be 10 digits."))
        ],
        max_length=10,
        blank=True,
        verbose_name=_("phone number"),
    )
    avatar = models.ForeignKey(
        "common.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("avatar"),
    )
