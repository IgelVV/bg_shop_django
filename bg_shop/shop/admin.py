from django import forms
from django.db import models as db_models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shop import models, services


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ("depth",)
    list_display = ('pk', 'title', 'parent_id', 'is_active')
    list_display_links = ('pk', 'title',)
    actions = ["delete_categories", "mark_as_active", "mark_as_inactive"]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.obj_depth_for_formfield = None
        self.obj_pk_for_formfield = None

    def save_model(self, request, obj, form: forms.Form, change):
        service = services.CategoryService()
        form_data = form.cleaned_data
        service.update_or_create(instance=obj, **form_data)

    def delete_model(self, request, obj):
        service = services.CategoryService()
        service.delete(instance=obj, hard=True)

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    @admin.action(description=_("Delete categories"))
    def delete_categories(self, request, queryset) -> None:
        for obj in queryset:
            self.delete_model(request=request, obj=obj)

    @admin.action(description=_("Mark as active"))
    def mark_as_active(self, request, queryset) -> None:
        for obj in queryset:
            obj.is_active = True
            obj.save()

    @admin.action(description=_("Mark as inactive"))
    def mark_as_inactive(self, request, queryset) -> None:
        for obj in queryset:
            obj.is_active = False
            obj.save()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.obj_pk_for_formfield = obj.pk
            self.obj_depth_for_formfield = obj.depth
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restricts binding to itself,
        or to category of the same level or higher.
        Allow setting parent with higher level if previous parent was None.
        """
        if db_field.name == "parent":
            depth = self.obj_depth_for_formfield \
                    or services.CategoryService().get_max_depth()
            kwargs["queryset"] = models.Category.objects\
                .filter(~db_models.Q(pk=self.obj_pk_for_formfield))\
                .filter(depth__lt=depth)\
                .filter(is_active=True)
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


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    ...
