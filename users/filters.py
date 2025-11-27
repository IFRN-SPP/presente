import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Email"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Sobrenome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    type = django_filters.ChoiceFilter(
        choices=User.UserType.choices,
        label=_("Tipo"),
        widget=forms.Select(
            attrs={"class": "form-select", "data-tom-select": "simple"}
        ),
    )
    is_active = django_filters.BooleanFilter(
        label=_("Ativo"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "type", "is_active"]
