from django.contrib import admin
from dynamic_config import models
from django.urls import reverse
from django import http


@admin.register(models.DynamicConfig)
class DynamicConfigAdmin(admin.ModelAdmin):
    def response_post_save_change(self, request, obj):
        return http.HttpResponseRedirect(
            reverse(
                "admin:dynamic_config_dynamicconfig_change",
                kwargs={"object_id": obj.id}
            )
        )

    def changelist_view(self, request, extra_context=None):
        super().changelist_view(request, extra_context)
        return http.HttpResponseRedirect(
            reverse(
                "admin:dynamic_config_dynamicconfig_change",
                kwargs={"object_id": 1}
            )
        )
