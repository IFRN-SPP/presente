import django_filters
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import User


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Email"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Sobrenome"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )
    groups = django_filters.ModelChoiceFilter(
        queryset=Group.objects.all(),
        label=_("Grupo"),
        widget=django_filters.widgets.forms.Select(attrs={"class": "form-select"}),
    )
    is_active = django_filters.BooleanFilter(
        label=_("Ativo"),
        widget=django_filters.widgets.forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "groups", "is_active"]


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Nome"),
        widget=django_filters.widgets.forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Group
        fields = ["name"]
