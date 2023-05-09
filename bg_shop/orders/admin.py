from django.contrib import admin
from orders import models
from shop import models as shop_models

#
# class ProductInline(admin.StackedInline):
#     model = shop_models.Product


class OrderedProductInline(admin.TabularInline):
    model = models.OrderedProduct


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderedProductInline,)


@admin.register(models.OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    # inlines = (ProductInline,)
    ...

