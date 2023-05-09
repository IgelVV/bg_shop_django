from django.contrib import admin
from shop import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Specification)
class SpecificationAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    ...
