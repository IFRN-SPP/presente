import django_filters
from django.utils.translation import gettext_lazy as _
from .models import Event, Activity


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
