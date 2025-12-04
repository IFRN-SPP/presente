import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import User


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        method="filter_name",
        label=_("Nome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    type = django_filters.ChoiceFilter(
        choices=User.UserType.choices,
        label=_("Tipo"),
        empty_label="---------",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    campus = django_filters.ChoiceFilter(
        label=_("Campus"),
        choices=lambda: [
            (campus, campus)
            for campus in User.objects.exclude(campus__isnull=True)
            .exclude(campus="")
            .values_list("campus", flat=True)
            .distinct()
            .order_by("campus")
        ],
        empty_label="---------",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    curso = django_filters.ChoiceFilter(
        label=_("Curso"),
        choices=lambda: [
            (curso, curso)
            for curso in User.objects.exclude(curso__isnull=True)
            .exclude(curso="")
            .values_list("curso", flat=True)
            .distinct()
            .order_by("curso")
        ],
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    periodo_referencia = django_filters.ChoiceFilter(
        label=_("Período"),
        choices=lambda: [
            (periodo, periodo)
            for periodo in User.objects.exclude(periodo_referencia__isnull=True)
            .exclude(periodo_referencia="")
            .values_list("periodo_referencia", flat=True)
            .distinct()
            .order_by("periodo_referencia")
        ],
        empty_label="---------",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    class Meta:
        model = User
        fields = [
            "name",
            "type",
            "campus",
            "curso",
            "periodo_referencia",
        ]
