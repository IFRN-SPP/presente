from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from core.mixins import PageTitleMixin, SuperuserRequiredMixin
from core.views import (
    CoreCreateView,
    CoreDetailView,
    CoreUpdateView,
    CoreDeleteView,
    CoreFilterView,
)
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from .models import Activity, Attendance
from .tables import ActivityTable, AttendanceTable, ActivityAttendanceTable
from .forms import ActivityForm, AttendancePrintConfigForm
from .filters import ActivityFilter, AttendanceFilter, ActivityAttendanceFilter
from .mixins import ActivityOwnerMixin
from .utils import (
    get_client_ip,
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


class ActivityListView(CoreFilterView):
    page_title = _("Minhas Atividades")
    model = Activity
    table_class = ActivityTable
    filterset_class = ActivityFilter
    permission_required = []

    def get_queryset(self):
        return Activity.objects.filter(owners=self.request.user)


class AdminActivitiesView(SuperuserRequiredMixin, CoreFilterView):
    page_title = _("Atividades")
    model = Activity
    table_class = ActivityTable
    filterset_class = ActivityFilter


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

    def get_success_url(self):
        return reverse_lazy("presente:activity_view", kwargs={"pk": self.kwargs["pk"]})

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
    template_name = "presente/public_activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encoded_id = kwargs.get("encoded_id")

        activity_id = decode_activity_id(encoded_id)
        if not activity_id:
            raise Http404("Activity not found")

        activity = get_object_or_404(Activity, id=activity_id, is_enabled=True)

        context["activity"] = activity
        context["encoded_id"] = encoded_id

        return context


class ActivityQRCodeView(TemplateView):
    template_name = "presente/includes/qr_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encoded_id = kwargs.get("encoded_id")
        now = timezone.now()

        context["server_time"] = now.isoformat()
        context["encoded_id"] = encoded_id

        activity_id = decode_activity_id(encoded_id)
        if activity_id:
            activity = get_object_or_404(Activity, id=activity_id)
            context["activity"] = activity

            # Pre-calculate countdown for not_started activities
            if activity.status == "not_started":
                seconds_until_start = int((activity.start_time - now).total_seconds())
                context["seconds_until_start"] = max(0, seconds_until_start)

            if activity.status == "active":
                checkin_token = generate_checkin_token(activity.id, activity.qr_timeout)
                checkin_path = reverse(
                    "presente:checkin", kwargs={"token": checkin_token}
                )
                checkin_url = self.request.build_absolute_uri(checkin_path)

                # Generate QR code server-side
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=1,
                )
                qr.add_data(checkin_url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_data_url = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

                context.update(
                    {
                        "checkin_url": checkin_url,
                        "qr_data_url": qr_data_url,
                        "timeout": activity.qr_timeout,
                    }
                )

        return context


class CheckInView(LoginRequiredMixin, TemplateView):
    template_name = "presente/checkin_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = kwargs.get("token")
        context["success"] = False

        activity_id = verify_checkin_token(token, 300)

        if not activity_id:
            context["error"] = _("QR Code inválido ou expirado.")
        else:
            activity = get_object_or_404(Activity, id=activity_id)
            client_ip = get_client_ip(self.request)

            context["activity"] = activity
            context["encoded_id"] = encode_activity_id(activity.id)

            if not activity.is_ip_allowed(client_ip):
                context["error"] = _(
                    "Acesso negado. Seu IP ({ip}) não tem permissão para registrar presença nesta atividade."
                ).format(ip=client_ip)
                context["client_ip"] = client_ip
            elif activity.status == "not_started":
                context["error"] = _(
                    "Esta atividade ainda não começou. Não é possível registrar presença."
                )
            elif activity.status == "expired":
                context["error"] = _(
                    "Esta atividade já encerrou. Não é mais possível registrar presença."
                )
            elif activity.status == "not_enabled":
                context["error"] = _("Esta atividade não está aceitando presenças.")
            elif not verify_checkin_token(token, activity.qr_timeout):
                context["error"] = _("QR Code expirado. Solicite um novo código.")
            else:
                attendance, created = Attendance.objects.get_or_create(
                    activity=activity,
                    user=self.request.user,
                    defaults={"ip_address": client_ip},
                )

                context.update(
                    {
                        "success": True,
                        "attendance": attendance,
                        "created": created,
                    }
                )

        return context


class MyAttendancesView(CoreFilterView):
    page_title = _("Minhas Presenças")
    model = Attendance
    table_class = AttendanceTable
    filterset_class = AttendanceFilter
    table_pagination = {"per_page": 20}
    actions = []
    permission_required = []

    def get_queryset(self):
        return (
            Attendance.objects.filter(user=self.request.user)
            .select_related("activity")
            .prefetch_related("activity__tags")
            .order_by("-checked_in_at")
        )


class ActivityAttendanceListView(ActivityOwnerMixin, CoreFilterView):
    model = Attendance
    table_class = ActivityAttendanceTable
    filterset_class = ActivityAttendanceFilter
    template_name = "presente/activity_attendance_list.html"
    table_pagination = {"per_page": 20}
    # context_object_name = "attendances"
    actions = ["delete"]
    permission_required = []

    def get_page_title(self):
        activity = self.get_activity()
        return _("Presenças - {}").format(activity.title)

    def get_queryset(self):
        activity = self.get_activity()
        return (
            Attendance.objects.filter(activity=activity)
            .select_related("user")
            .order_by("-checked_in_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.get_activity()
        context["activity"] = activity
        context["total_attendances"] = self.get_queryset().count()
        return context

    def get_allowed_actions(self):
        allowed_actions = {}
        allowed_actions["delete"] = "presente:attendance_delete"
        return allowed_actions


class AttendanceDeleteView(CoreDeleteView):
    model = Attendance
    success_message = _("Presença removida com sucesso!")
    permission_required = []

    def get_queryset(self):
        # Get the attendance and check if user is owner of the activity or superuser
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_pk"])

        # Check if user is owner or superuser
        if (
            not self.request.user.is_superuser
            and not activity.owners.filter(pk=self.request.user.pk).exists()
        ):
            raise Http404(
                "Você não tem permissão para remover presenças desta atividade"
            )

        return Attendance.objects.filter(activity=activity)

    def get_success_url(self):
        return reverse_lazy(
            "presente:activity_attendances", kwargs={"pk": self.kwargs["activity_pk"]}
        )


class ActivityAttendancePrintConfigView(
    ActivityOwnerMixin,
    LoginRequiredMixin,
    TemplateView,
):
    template_name = "presente/includes/attendance_print_config_modal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.get_activity()
        context["activity"] = activity
        context["form"] = AttendancePrintConfigForm()

        # Convert GET params to dict for easier template iteration
        filter_params = {}
        for key, value in self.request.GET.items():
            if key not in ["columns", "sort_by"]:
                filter_params[key] = value
        context["filter_params"] = filter_params

        return context


class ActivityAttendancePrintView(
    ActivityOwnerMixin,
    LoginRequiredMixin,
    FilterView,
):
    model = Attendance
    filterset_class = ActivityAttendanceFilter
    template_name = "presente/attendance_print.html"
    context_object_name = "attendances"

    def get_queryset(self):
        activity = self.get_activity()

        # Get base queryset
        qs = Attendance.objects.filter(activity=activity).select_related("user")

        # Apply sorting from configuration
        sort_by = self.request.GET.get("sort_by", "name")
        if sort_by:
            # Map sort fields to actual model fields
            sort_mapping = {
                "name": "user__full_name",
                "-name": "-user__full_name",
                "type": "user__type",
                "-type": "-user__type",
                "curso": "user__curso",
                "-curso": "-user__curso",
                "checked_in_at": "checked_in_at",
                "-checked_in_at": "-checked_in_at",
            }
            sort_field = sort_mapping.get(sort_by, "user__full_name")
            qs = qs.order_by(sort_field)
        else:
            qs = qs.order_by("user__full_name")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.get_activity()
        context["activity"] = activity

        # Get the filtered queryset (after filters are applied)
        filtered_qs = context["filter"].qs
        context["total_attendances"] = filtered_qs.count()

        # Get column configuration
        columns = self.request.GET.getlist("columns")
        if not columns:
            columns = ["number", "name", "matricula", "checked_in_at"]
        context["columns"] = columns

        # Get sort configuration
        context["sort_by"] = self.request.GET.get("sort_by", "name")

        # Get filter information for display
        filter_info = []
        filter_data = self.request.GET

        if filter_data.get("user__full_name"):
            filter_info.append(f"Nome: {filter_data['user__full_name']}")
        if filter_data.get("user__type"):
            type_display = dict(User.UserType.choices).get(filter_data["user__type"])
            filter_info.append(f"Tipo: {type_display}")
        if filter_data.get("user__curso"):
            filter_info.append(f"Curso: {filter_data['user__curso']}")
        if filter_data.get("user__periodo_referencia"):
            filter_info.append(f"Período: {filter_data['user__periodo_referencia']}")

        context["filter_info"] = filter_info
        context["generated_at"] = timezone.now()

        return context
