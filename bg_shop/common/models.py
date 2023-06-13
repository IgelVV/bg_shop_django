from django.db import models
from django.utils.translation import gettext_lazy as _


class Image(models.Model):
    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")

    description = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("description"),
    )
    img = models.ImageField(
        upload_to='images',
        verbose_name=_("image")
    )

    def __str__(self):
        return f"Image({self.pk}): {self.description[:10]}"
