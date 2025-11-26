import django_filters
from django.utils.translation import gettext_lazy as _
from .models import Event, Activity, Attendance


class EventFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    is_published = django_filters.BooleanFilter(
        label=_("Publicado"),
        widget=django_filters.widgets.forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
    )

    class Meta:
        model = Event
        fields = ["name", "is_published"]


class ActivityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Título"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    event = django_filters.ModelChoiceFilter(
        queryset=Event.objects.all(),
        label=_("Evento"),
        widget=django_filters.widgets.forms.Select(attrs={"class": "form-select"}),
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
            "event",
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
    activity__event = django_filters.ModelChoiceFilter(
        queryset=Event.objects.none(),  # Will be set in __init__
        label=_("Evento"),
        widget=django_filters.widgets.forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show events that the user has attended
        if self.request:
            user_events = Event.objects.filter(
                activities__attendances__user=self.request.user
            ).distinct()
            self.filters["activity__event"].queryset = user_events

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
            "activity__event",
            "checked_in_at__gte",
            "checked_in_at__lte",
            "activity__start_time__gte",
            "activity__start_time__lte",
        ]
