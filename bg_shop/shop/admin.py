from django import forms
from django.db import models as db_models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shop import models, services


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'count', 'is_active',)
    list_display_links = ('pk', 'title',)


class ProductInline(admin.TabularInline):
    model = models.Product
    fk_name = "category"
    extra = 0
    can_delete = False
    max_num = 0

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    """Represents tree structure of Category model"""
    inlines = (ProductInline,)
    readonly_fields = ("depth",)
    list_display = ('pk', 'title', 'parent_id', 'is_active')
    list_display_links = ('pk', 'title',)
    actions = ["delete_categories", "mark_as_active", "mark_as_inactive"]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.obj_depth_for_formfield = None
        self.obj_pk_for_formfield = None

    def get_queryset(self, request):
        """Cashes related Products."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('product_set')

    def save_model(self, request, obj, form: forms.Form, change):
        """Overrides for using service instead of model methods."""
        service = services.CategoryService()
        form_data = form.cleaned_data
        service.update_or_create(instance=obj, **form_data)

    def delete_model(self, request, obj):
        """Overrides for using service instead of model methods."""
        service = services.CategoryService()
        service.delete(instance=obj, hard=True)

    def get_actions(self, request):
        """Overriden to remove `delete_selected` action"""
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    @admin.action(description=_("Delete categories"))
    def delete_categories(self, request, queryset) -> None:
        """To bulk delete Categories"""
        for obj in queryset:
            self.delete_model(request=request, obj=obj)

    @admin.action(description=_("Mark as active"))
    def mark_as_active(self, request, queryset) -> None:
        """Sets `is_active` field as True"""
        for obj in queryset:
            obj.is_active = True
            obj.save()

    @admin.action(description=_("Mark as inactive"))
    def mark_as_inactive(self, request, queryset) -> None:
        """Sets `is_active` field as True"""
        for obj in queryset:
            obj.is_active = False
            obj.save()

    def get_form(self, request, obj=None, **kwargs):
        """Overriden to add new fields to admin form
        to use in other methods."""
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
    list_display = ('pk', 'author', 'product', 'rate')
    list_display_links = ('pk',)


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'discount', 'date_from', 'date_to',)
    list_display_links = ('pk', 'product')


@admin.register(models.Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'value')
    list_display_links = ('pk', 'name')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product',)
    list_display_links = ('pk', 'product')
