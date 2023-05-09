from django.contrib import admin
from common import models


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    ...
