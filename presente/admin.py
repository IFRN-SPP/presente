from django.contrib import admin
from .models import Activity, Attendance, Network


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    fieldsets = (
        (None, {"fields": ("name", "description", "is_active")}),
        ("Endereços IP", {"fields": ("ip_addresses",)}),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "start_time",
        "end_time",
        "qr_timeout",
    ]
    list_filter = ["tags"]
    search_fields = ["title"]
    date_hierarchy = "start_time"
    filter_horizontal = ["owners", "allowed_networks"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["user", "activity", "checked_in_at", "network_or_ip"]
    list_filter = ["activity", "checked_in_at"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "activity__title",
        "ip_address",
    ]
    date_hierarchy = "checked_in_at"
    readonly_fields = ["checked_in_at", "ip_address", "network_display"]

    def network_or_ip(self, obj):
        return obj.get_network_name()

    network_or_ip.short_description = "Rede/IP"

    def network_display(self, obj):
        if not obj.ip_address:
            return "-"
        network_name = obj.get_network_name()
        if network_name != obj.ip_address:
            return f"{network_name} ({obj.ip_address})"
        return obj.ip_address

    network_display.short_description = "Rede"
