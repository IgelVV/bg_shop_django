from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from account import models

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = models.Profile


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username", "first_name", "last_name", "email", "is_staff",
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
