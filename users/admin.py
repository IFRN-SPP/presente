from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    readonly_fields = BaseUserAdmin.readonly_fields + (
        "type",
        "avatar_url",
        "is_suap_user",
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Informações SUAP", {"fields": ("is_suap_user", "type", "avatar_url")}),
    )

    list_display = BaseUserAdmin.list_display + ("type", "is_suap_user")
    list_filter = BaseUserAdmin.list_filter + ("type", "is_suap_user")


admin.site.register(User, UserAdmin)
