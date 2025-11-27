from django.contrib import admin
from .models import Activity, Attendance


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "start_time",
        "end_time",
        "is_published",
        "qr_timeout",
    ]
    list_filter = ["is_published", "tags"]
    search_fields = ["title"]
    date_hierarchy = "start_time"
    filter_horizontal = ["owners"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["user", "activity", "checked_in_at"]
    list_filter = ["activity", "checked_in_at"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "activity__title",
    ]
    date_hierarchy = "checked_in_at"
    readonly_fields = ["checked_in_at"]
