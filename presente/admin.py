from django.contrib import admin
from .models import Event, Activity, Attendance


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "is_published"]
    list_filter = ["is_published"]
    search_fields = ["name", "description"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "event",
        "start_time",
        "end_time",
        "is_published",
        "qr_timeout",
    ]
    list_filter = ["is_published", "event"]
    search_fields = ["title"]
    date_hierarchy = "start_time"


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
