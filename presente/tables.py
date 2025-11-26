import django_tables2
from django.utils.translation import gettext_lazy as _
from .models import Event, Activity


class CoreTable(django_tables2.Table):
    actions = django_tables2.TemplateColumn(
        template_name="core/includes/actions.html",
        orderable=False,
        verbose_name=_("Ações"),
        exclude_from_export=True,
    )


class EventTable(CoreTable):
    class Meta:
        model = Event
        fields = ("name", "description", "is_published")


class ActivityTable(CoreTable):
    class Meta:
        model = Activity
        fields = ("event", "title", "start_time", "end_time", "is_published")
