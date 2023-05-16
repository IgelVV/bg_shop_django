from django.contrib import admin
from django.db import models as db_models
from shop import models, services


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    # readonly_fields = ("depth",)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.obj_depth_for_formfield = None
        self.obj_pk_for_formfield = None

    # def save_model(self, request, obj, form, change):
    #     ... #use service

    # def delete_model(self, request, obj):
        ...

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.obj_pk_for_formfield = obj.pk
            self.obj_depth_for_formfield = obj.depth
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        To restrict binding to itself,
        of to category of the same level or less.
        """
        if db_field.name == "parent":
            depth = self.obj_depth_for_formfield \
                    or services.CategoryService().get_max_depth()
            kwargs["queryset"] = models.Category.objects\
                .filter(~db_models.Q(pk=self.obj_pk_for_formfield))\
                .filter(depth__lt=depth)
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
