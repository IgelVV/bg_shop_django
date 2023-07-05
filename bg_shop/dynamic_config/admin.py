from django.contrib import admin
from dynamic_config import models
from django.urls import reverse
from django import http


@admin.register(models.DynamicConfig)
class DynamicConfigAdmin(admin.ModelAdmin):
    """
    Admin panel for singleton dynamic config.

    Overrides standard ModelAdmin methods to represent singleton model
    in Admin. It redirects on object_change view from changelist view,
    and from add view. It allows to save and change only obj with id=1.
    """

    exclude = ("id",)

    def response_post_save_change(self, request, obj):
        """
        Redirects to change page again
        :param request: django request
        :param obj: instance of DynamicConfig which had been saved
        :return:
        """
        return http.HttpResponseRedirect(
            reverse(
                "admin:dynamic_config_dynamicconfig_change",
                kwargs={"object_id": obj.id}
            )
        )

    def changelist_view(self, request, extra_context=None):
        """Redirects to obj_change view"""
        return http.HttpResponseRedirect(
            reverse(
                "admin:dynamic_config_dynamicconfig_change",
                kwargs={"object_id": 1}
            )
        )

    def add_view(self, request, form_url="", extra_context=None):
        """Redirects to obj_change view"""
        return http.HttpResponseRedirect(
            reverse(
                "admin:dynamic_config_dynamicconfig_change",
                kwargs={"object_id": 1}
            )
        )

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of singleton instance."""
        return False

    def render_change_form(
            self,
            request,
            context,
            add=False,
            change=False,
            form_url='',
            obj=None
    ):
        """Remove useless buttons."""
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False
        })
        return super().render_change_form(
            request, context, add, change, form_url, obj)
