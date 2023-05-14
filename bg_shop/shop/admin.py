from django.contrib import admin
from django.db import models as db_models
from shop import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.my_pk_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.my_pk_for_formfield = obj.pk
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = models.Category.objects.filter(
                ~db_models.Q(pk=self.my_pk_for_formfield))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
