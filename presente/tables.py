import django_tables2
from django.utils.translation import gettext_lazy as _
from .models import Event, Activity, Attendance


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


class AttendanceTable(django_tables2.Table):
    activity_title = django_tables2.Column(
        accessor="activity__title",
        verbose_name=_("Atividade"),
        orderable=True,
    )
    event_name = django_tables2.Column(
        accessor="activity__event__name",
        verbose_name=_("Evento"),
        orderable=True,
    )
    activity_start = django_tables2.DateTimeColumn(
        accessor="activity__start_time",
        verbose_name=_("Início da Atividade"),
        format="d/m/Y H:i",
        orderable=True,
    )
    activity_end = django_tables2.DateTimeColumn(
        accessor="activity__end_time",
        verbose_name=_("Término da Atividade"),
        format="d/m/Y H:i",
        orderable=True,
    )
    checked_in_at = django_tables2.DateTimeColumn(
        verbose_name=_("Presença Registrada em"),
        format="d/m/Y H:i:s",
        orderable=True,
    )

    class Meta:
        model = Attendance
        fields = (
            "activity_title",
            "event_name",
            "activity_start",
            "activity_end",
            "checked_in_at",
        )
        order_by = "-checked_in_at"
