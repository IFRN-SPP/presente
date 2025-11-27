import django_tables2
from django.utils.translation import gettext_lazy as _
from .models import Activity, Attendance


class CoreTable(django_tables2.Table):
    actions = django_tables2.TemplateColumn(
        template_name="core/includes/actions.html",
        orderable=False,
        verbose_name=_("Ações"),
        exclude_from_export=True,
    )


class ActivityTable(CoreTable):
    tags_list = django_tables2.TemplateColumn(
        template_name="presente/includes/tags_column.html",
        verbose_name=_("Tags"),
        orderable=False,
        exclude_from_export=True,
    )

    class Meta:
        model = Activity
        fields = ("title", "tags_list", "start_time", "end_time", "is_published")


class AttendanceTable(django_tables2.Table):
    activity_title = django_tables2.Column(
        accessor="activity__title",
        verbose_name=_("Atividade"),
        orderable=True,
    )
    activity_tags = django_tables2.TemplateColumn(
        template_name="presente/includes/tags_column_attendance.html",
        verbose_name=_("Tags"),
        orderable=False,
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
            "activity_tags",
            "activity_start",
            "activity_end",
            "checked_in_at",
        )
        order_by = "-checked_in_at"


class ActivityAttendanceTable(django_tables2.Table):
    user_name = django_tables2.Column(
        accessor="user__first_name",
        verbose_name=_("Nome"),
        orderable=True,
    )
    user_email = django_tables2.Column(
        accessor="user__email",
        verbose_name=_("E-mail"),
        orderable=True,
    )
    user_type = django_tables2.Column(
        accessor="user__type",
        verbose_name=_("Tipo"),
        orderable=True,
    )
    checked_in_at = django_tables2.DateTimeColumn(
        verbose_name=_("Presença Registrada em"),
        format="d/m/Y H:i:s",
        orderable=True,
    )
    actions = django_tables2.TemplateColumn(
        template_name="presente/includes/attendance_actions.html",
        orderable=False,
        verbose_name=_("Ações"),
        exclude_from_export=True,
    )

    class Meta:
        model = Attendance
        fields = (
            "user_name",
            "user_email",
            "user_type",
            "checked_in_at",
        )
        order_by = "-checked_in_at"
