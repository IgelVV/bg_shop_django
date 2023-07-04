"""Models that are used in different parts of the project."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from common import validators


# todo delete image from media when delete()
class Image(models.Model):
    """All images used in other models."""

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
        validators=[
            validators.FileMaxSizeValidator(
                message=_(
                    f"Max file size is {settings.MAX_IMAGE_SIZE/1024}KB"),
                limit_value=settings.MAX_IMAGE_SIZE,
            ),
        ],
        verbose_name=_("image"),
    )

    def __str__(self):
        return f"Image({self.pk}): {self.description[:10]}"
