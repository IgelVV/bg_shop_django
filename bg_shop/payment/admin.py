from django.contrib import admin
from payment import models


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    ...


