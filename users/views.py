from allauth.account.views import PasswordResetFromKeyView
from django.urls import reverse_lazy
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from core.mixins import PageTitleMixin, AutoPermissionRequiredMixin, AllowedActionsMixin
from core.views import (
    CoreCreateView,
    CoreDetailView,
    CoreUpdateView,
    CoreDeleteView,
)
from .tables import UserTable, GroupTable
from .filters import UserFilter, GroupFilter

User = get_user_model()


class ExcludeAdminMixin:
    admin_id = 1

    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.exclude(id=self.admin_id).order_by("id")


class FilterPermissionsMixin:
    allowed_apps = ["auth", "users", "core"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["permissions"].queryset = Permission.objects.filter(
            content_type__app_label__in=self.allowed_apps
        )
        return form


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    success_url = reverse_lazy("account_login")


class UserListView(
    ExcludeAdminMixin,
    AutoPermissionRequiredMixin,
    AllowedActionsMixin,
    PageTitleMixin,
    SingleTableMixin,
    FilterView,
):
    page_title = _("Usuários")
    paginate_by = 10
    model = User
    table_class = UserTable
    filterset_class = UserFilter
    template_name = "core/list.html"
    permission_action = "view"


class UserCreateView(CoreCreateView):
    page_title = _("Usuários")
    model = User
    fields = ["email", "first_name", "last_name", "groups"]


class UserDetailView(ExcludeAdminMixin, CoreDetailView):
    page_title = _("Usuários")
    model = User
    context_object_name = "user_obj"
    fields = ["email", "first_name", "last_name", "groups", "last_login"]


class UserUpdateView(ExcludeAdminMixin, CoreUpdateView):
    page_title = _("Usuários")
    model = User
    context_object_name = "user_obj"
    fields = ["email", "first_name", "last_name", "groups"]


class UserDeleteView(ExcludeAdminMixin, CoreDeleteView):
    model = User
    context_object_name = "user_obj"


class GroupListView(
    AutoPermissionRequiredMixin,
    AllowedActionsMixin,
    PageTitleMixin,
    SingleTableMixin,
    FilterView,
):
    page_title = _("Grupos")
    paginate_by = 10
    model = Group
    table_class = GroupTable
    filterset_class = GroupFilter
    template_name = "core/list.html"
    permission_action = "view"

    def get_queryset(self):
        return Group.objects.all().order_by("name")


class GroupCreateView(FilterPermissionsMixin, CoreCreateView):
    page_title = _("Grupos")
    model = Group
    fields = "__all__"


class GroupDetailView(CoreDetailView):
    page_title = _("Grupos")
    model = Group
    fields = "__all__"


class GroupUpdateView(FilterPermissionsMixin, CoreUpdateView):
    page_title = _("Grupos")
    model = Group
    fields = "__all__"


class GroupDeleteView(CoreDeleteView):
    model = Group


class UserProfileView(LoginRequiredMixin, PageTitleMixin, TemplateView):
    page_title = _("Perfil")
    template_name = "presente/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class UserProfileUpdateView(LoginRequiredMixin, PageTitleMixin, UpdateView):
    page_title = _("Atualizar Perfil")
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "presente/profile_edit.html"
    success_url = reverse_lazy("core:user_profile")

    def get_object(self, queryset=None):
        return self.request.user
