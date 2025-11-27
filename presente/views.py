from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.views.generic.edit import DeleteView
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from core.mixins import PageTitleMixin, AutoPermissionRequiredMixin, AllowedActionsMixin
from core.views import (
    CoreCreateView,
    CoreDetailView,
    CoreUpdateView,
    CoreDeleteView,
)
from .models import Activity, Attendance
from .tables import ActivityTable, AttendanceTable, ActivityAttendanceTable
from .forms import ActivityForm
from .filters import ActivityFilter, AttendanceFilter
from .utils import (
    encode_activity_id,
    decode_activity_id,
    generate_checkin_token,
    verify_checkin_token,
)

User = get_user_model()


class IndexView(LoginRequiredMixin, PageTitleMixin, TemplateView):
    template_name = "presente/index.html"
    page_title = _("Dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["activities"] = Activity.objects.count()
        else:
            context["activities"] = Activity.objects.filter(
                owners=self.request.user
            ).count()
        context["my_attendances_count"] = Attendance.objects.filter(
            user=self.request.user
        ).count()
        context["recent_attendances"] = (
            Attendance.objects.filter(user=self.request.user)
            .select_related("activity")
            .order_by("-checked_in_at")[:5]
        )
        return context


class ActivityListView(
    AutoPermissionRequiredMixin,
    AllowedActionsMixin,
    PageTitleMixin,
    SingleTableMixin,
    FilterView,
):
    page_title = _("Atividades")
    paginate_by = 10
    model = Activity
    table_class = ActivityTable
    filterset_class = ActivityFilter
    template_name = "core/list.html"
    permission_action = "view"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Activity.objects.all()
        return Activity.objects.filter(owners=self.request.user)


class ActivityCreateView(CoreCreateView):
    model = Activity
    page_title = _("Atividades")
    form_class = ActivityForm

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.owners.add(self.request.user)
        return response


class ActivityDetailView(CoreDetailView):
    model = Activity
    page_title = _("Atividades")
    template_name = "presente/activity_detail.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Activity.objects.all()
        return Activity.objects.filter(owners=self.request.user)

    def get_fields(self):
        fields = super().get_fields()
        # Add owners to the fields list
        owners_list = ", ".join(
            [owner.get_full_name() or owner.email for owner in self.object.owners.all()]
        )
        fields.append(
            {
                "label": _("Responsáveis"),
                "value": owners_list if owners_list else "-",
                "safe": False,
            }
        )
        return fields

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = self.object.attendances.select_related("user").all()
        context["encoded_id"] = encode_activity_id(self.object.id)
        return context


class ActivityUpdateView(CoreUpdateView):
    model = Activity
    page_title = _("Atividades")
    form_class = ActivityForm

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Activity.objects.all()
        return Activity.objects.filter(owners=self.request.user)


class ActivityDeleteView(CoreDeleteView):
    model = Activity

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Activity.objects.all()
        return Activity.objects.filter(owners=self.request.user)


# Public views for attendance


class PublicActivityView(TemplateView):
    """Public page showing activity details and QR code for check-in"""

    template_name = "presente/public_activity.html"

    def get(self, request, encoded_id):
        activity_id = decode_activity_id(encoded_id)
        if not activity_id:
            raise Http404("Activity not found")

        activity = get_object_or_404(Activity, id=activity_id, is_published=True)

        return render(
            request,
            self.template_name,
            {
                "activity": activity,
                "encoded_id": encoded_id,
            },
        )


class ActivityQRCodeView(View):
    """HTMX endpoint that generates a new time-based QR code token"""

    def get(self, request, encoded_id):
        activity_id = decode_activity_id(encoded_id)
        if not activity_id:
            return render(request, "presente/includes/qr_error.html", status=404)

        activity = get_object_or_404(Activity, id=activity_id, is_published=True)
        checkin_token = generate_checkin_token(activity.id, activity.qr_timeout)
        checkin_path = reverse("presente:checkin", kwargs={"token": checkin_token})
        checkin_url = request.build_absolute_uri(checkin_path)

        return render(
            request,
            "presente/includes/qr_code.html",
            {
                "checkin_url": checkin_url,
                "activity": activity,
                "timeout": activity.qr_timeout,
                "encoded_id": encoded_id,
            },
        )


class CheckInView(LoginRequiredMixin, View):
    """View that registers user attendance when they scan the QR code"""

    def get(self, request, token):
        activity_id = verify_checkin_token(token, 300)  # Max 5 min for safety

        if not activity_id:
            messages.error(request, _("QR Code inválido ou expirado."))
            return render(
                request,
                "presente/checkin_error.html",
                {"error": _("QR Code inválido ou expirado.")},
            )

        activity = get_object_or_404(Activity, id=activity_id)

        # Verify token with activity's timeout
        activity_id_verified = verify_checkin_token(token, activity.qr_timeout)
        if not activity_id_verified:
            messages.error(request, _("QR Code expirado. Solicite um novo código."))
            return render(
                request,
                "presente/checkin_error.html",
                {
                    "error": _("QR Code expirado. Solicite um novo código."),
                    "activity": activity,
                    "encoded_id": encode_activity_id(activity.id),
                },
            )

        # Check if user already checked in
        attendance, created = Attendance.objects.get_or_create(
            activity=activity, user=request.user
        )

        if created:
            messages.success(request, _("Presença registrada com sucesso!"))
        else:
            messages.info(request, _("Você já registrou presença nesta atividade."))

        return render(
            request,
            "presente/checkin_success.html",
            {
                "activity": activity,
                "attendance": attendance,
                "created": created,
            },
        )


class MyAttendancesView(
    LoginRequiredMixin,
    PageTitleMixin,
    SingleTableMixin,
    FilterView,
):
    """View showing the current user's attendances"""

    page_title = _("Minhas Presenças")
    model = Attendance
    table_class = AttendanceTable
    filterset_class = AttendanceFilter
    template_name = "core/list.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            Attendance.objects.filter(user=self.request.user)
            .select_related("activity")
            .prefetch_related("activity__tags")
            .order_by("-checked_in_at")
        )


class ActivityAttendanceListView(
    LoginRequiredMixin,
    PageTitleMixin,
    AllowedActionsMixin,
    SingleTableMixin,
    FilterView,
):
    """View showing all attendances for a specific activity"""

    model = Attendance
    table_class = ActivityAttendanceTable
    template_name = "core/list.html"
    paginate_by = 20
    context_object_name = "attendances"
    actions = ["delete"]

    def get_page_title(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["pk"])
        return _("Presenças - {}").format(activity.title)

    def get_queryset(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["pk"])

        # Check if user is owner (only owners can view attendances)
        if not activity.owners.filter(pk=self.request.user.pk).exists():
            raise Http404(
                "Você não tem permissão para ver as presenças desta atividade"
            )

        return (
            Attendance.objects.filter(activity=activity)
            .select_related("user")
            .order_by("-checked_in_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = get_object_or_404(Activity, pk=self.kwargs["pk"])
        context["activity"] = activity
        context["total_attendances"] = self.get_queryset().count()
        return context

    def get_allowed_actions(self):
        """Override to provide custom delete URL that includes activity pk"""
        allowed_actions = {}
        # Only add delete action for owners
        allowed_actions["delete"] = "presente:attendance_delete"
        return allowed_actions


class AttendanceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Delete an attendance - only accessible by activity owners"""

    model = Attendance
    template_name = "core/delete.html"
    template_name_modal = "core/includes/delete_modal.html"
    success_message = _("Presença removida com sucesso!")

    def get_queryset(self):
        # Get the attendance and check if user is owner of the activity
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_pk"])

        # Check if user is owner
        if not activity.owners.filter(pk=self.request.user.pk).exists():
            raise Http404(
                "Você não tem permissão para remover presenças desta atividade"
            )

        return Attendance.objects.filter(activity=activity)

    def get_success_url(self):
        return reverse_lazy(
            "presente:activity_attendances", kwargs={"pk": self.kwargs["activity_pk"]}
        )

    def get_template_names(self):
        if not self.request.htmx:
            return [self.template_name]
        return [self.template_name_modal]
