from django.contrib import admin
from orders import models


class OrderedProductInline(admin.TabularInline):
    model = models.OrderedProduct


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderedProductInline,)


@admin.register(models.OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    ...

