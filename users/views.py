from allauth.account.views import PasswordResetFromKeyView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from core.mixins import PageTitleMixin, AutoPermissionRequiredMixin, AllowedActionsMixin
from core.views import (
    CoreCreateView,
    CoreDetailView,
    CoreUpdateView,
    CoreDeleteView,
)
from .tables import UserTable
from .filters import UserFilter

User = get_user_model()


class ExcludeAdminMixin:
    admin_id = 1

    def get_queryset(self):
        base_qs = super().get_queryset()
        return base_qs.exclude(id=self.admin_id).order_by("id")


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
    fields = ["email", "first_name", "last_name"]


class UserDetailView(ExcludeAdminMixin, CoreDetailView):
    page_title = _("Usuários")
    model = User
    context_object_name = "user_obj"
    fields = ["email", "first_name", "last_name", "type", "last_login"]


class UserUpdateView(ExcludeAdminMixin, CoreUpdateView):
    page_title = _("Usuários")
    model = User
    context_object_name = "user_obj"
    fields = ["email", "first_name", "last_name"]


class UserDeleteView(ExcludeAdminMixin, CoreDeleteView):
    model = User
    context_object_name = "user_obj"


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
    success_url = reverse_lazy("users:user_profile")

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        # Prevent SUAP users from editing their profile
        if request.user.is_authenticated and request.user.is_suap_user:
            messages.warning(
                request,
                _(
                    "Seu perfil é gerenciado pelo SUAP e não pode ser editado manualmente. "
                    "Os dados são atualizados automaticamente a cada login."
                ),
            )
            return redirect("users:user_profile")
        return super().dispatch(request, *args, **kwargs)
