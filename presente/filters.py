import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from taggit.models import Tag
from .models import Activity, Attendance

User = get_user_model()


class ActivityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Título"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    tags = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        label=_("Tags"),
        field_name="tags",
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    start_time__gte = django_filters.DateFilter(
        field_name="start_time",
        lookup_expr="gte",
        label=_("Data inicial (a partir de)"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    start_time__lte = django_filters.DateFilter(
        field_name="start_time",
        lookup_expr="lte",
        label=_("Data inicial (até)"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    is_published = django_filters.BooleanFilter(
        label=_("Publicado"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
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
    """Filter for user's own attendances (My Attendances page)"""

    activity__title = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Atividade"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    activity__tags = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        label=_("Tags"),
        field_name="activity__tags",
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    user__full_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome do Usuário"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__email = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("E-mail do Usuário"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__type = django_filters.ChoiceFilter(
        choices=User.UserType.choices,
        label=_("Tipo de Usuário"),
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    user__curso = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Curso"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__periodo_referencia = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Período de Referência"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    checked_in_at__gte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="gte",
        label=_("Registrado a partir de"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    checked_in_at__lte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="lte",
        label=_("Registrado até"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    activity__start_time__gte = django_filters.DateFilter(
        field_name="activity__start_time",
        lookup_expr="gte",
        label=_("Atividade iniciada a partir de"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    activity__start_time__lte = django_filters.DateFilter(
        field_name="activity__start_time",
        lookup_expr="lte",
        label=_("Atividade iniciada até"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta:
        model = Attendance
        fields = [
            "activity__title",
            "activity__tags",
            "user__full_name",
            "user__email",
            "user__type",
            "user__curso",
            "user__periodo_referencia",
            "checked_in_at__gte",
            "checked_in_at__lte",
            "activity__start_time__gte",
            "activity__start_time__lte",
        ]


class ActivityAttendanceFilter(django_filters.FilterSet):
    """Filter for attendances of a specific activity"""

    user__full_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__email = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("E-mail"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__type = django_filters.ChoiceFilter(
        choices=User.UserType.choices,
        label=_("Tipo"),
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    user__curso = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Curso"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    user__periodo_referencia = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Período de Referência"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    checked_in_at__gte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="gte",
        label=_("Registrado a partir de"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    checked_in_at__lte = django_filters.DateFilter(
        field_name="checked_in_at",
        lookup_expr="lte",
        label=_("Registrado até"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta:
        model = Attendance
        fields = [
            "user__full_name",
            "user__email",
            "user__type",
            "user__curso",
            "user__periodo_referencia",
            "checked_in_at__gte",
            "checked_in_at__lte",
        ]
