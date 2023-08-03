from django.contrib import admin
from orders import models


class OrderedProductInline(admin.TabularInline):
    model = models.OrderedProduct


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderedProductInline,)
    list_display = (
        "pk",
        "created_at",
        "user",
        "status",
        "paid",
        "delivery_type",
        "is_active",
    )
    list_display_links = ('pk', 'created_at',)


@admin.register(models.OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    ...

