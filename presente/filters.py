import django_filters
from django.utils.translation import gettext_lazy as _
from .models import Activity, Attendance


class ActivityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Título"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    tags = django_filters.CharFilter(
        field_name="tags__name",
        lookup_expr="icontains",
        label=_("Tags"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    start_time__gte = django_filters.DateFilter(
        field_name="start_time",
        lookup_expr="gte",
        label=_("Data inicial (a partir de)"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    start_time__lte = django_filters.DateFilter(
        field_name="start_time",
        lookup_expr="lte",
        label=_("Data inicial (até)"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    is_published = django_filters.BooleanFilter(
        label=_("Publicado"),
        widget=django_filters.widgets.forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "tags",
            "start_time__gte",
            "start_time__lte",
            "is_published",
        ]


class AttendanceFilter(django_filters.FilterSet):
    activity__title = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Atividade"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    activity__tags = django_filters.CharFilter(
        field_name="activity__tags__name",
        lookup_expr="icontains",
        label=_("Tags"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )

    checked_in_at__gte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="gte",
        label=_("Registrado a partir de"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    checked_in_at__lte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="lte",
        label=_("Registrado até"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    activity__start_time__gte = django_filters.DateFilter(
        field_name="activity__start_time",
        lookup_expr="gte",
        label=_("Atividade iniciada a partir de"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )
    activity__start_time__lte = django_filters.DateFilter(
        field_name="activity__start_time",
        lookup_expr="lte",
        label=_("Atividade iniciada até"),
        widget=django_filters.widgets.forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )

    class Meta:
        model = Attendance
        fields = [
            "activity__title",
            "activity__tags",
            "checked_in_at__gte",
            "checked_in_at__lte",
            "activity__start_time__gte",
            "activity__start_time__lte",
        ]
