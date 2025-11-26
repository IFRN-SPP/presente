from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from core.mixins import PageTitleMixin, AutoPermissionRequiredMixin, AllowedActionsMixin
from core.views import (
    CoreCreateView,
    CoreDetailView,
    CoreUpdateView,
    CoreDeleteView,
)
from .models import Event, Activity, Attendance
from .tables import EventTable, ActivityTable
from .forms import EventForm, ActivityForm
from .filters import EventFilter, ActivityFilter
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
        context["events"] = Event.objects.filter(is_published=True).count()
        context["activities"] = Activity.objects.filter(is_published=True).count()
        return context


class EventListView(
    AutoPermissionRequiredMixin,
    AllowedActionsMixin,
    PageTitleMixin,
    SingleTableMixin,
    FilterView,
):
    page_title = _("Eventos")
    paginate_by = 10
    model = Event
    table_class = EventTable
    filterset_class = EventFilter
    template_name = "core/list.html"
    permission_action = "view"


class EventCreateView(CoreCreateView):
    page_title = _("Eventos")
    model = Event
    form_class = EventForm


class EventDetailView(CoreDetailView):
    page_title = _("Eventos")
    model = Event


class EventUpdateView(CoreUpdateView):
    page_title = _("Eventos")
    model = Event
    form_class = EventForm


class EventDeleteView(CoreDeleteView):
    model = Event


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


class ActivityCreateView(CoreCreateView):
    model = Activity
    page_title = _("Atividades")
    form_class = ActivityForm


class ActivityDetailView(CoreDetailView):
    model = Activity
    page_title = _("Atividades")
    template_name = "presente/activity_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = self.object.attendances.select_related("user").all()
        context["encoded_id"] = encode_activity_id(self.object.id)
        return context


class ActivityUpdateView(CoreUpdateView):
    model = Activity
    page_title = _("Atividades")
    form_class = ActivityForm


class ActivityDeleteView(CoreDeleteView):
    model = Activity


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
        checkin_url = request.build_absolute_uri(f"/presente/checkin/{checkin_token}/")

        return render(
            request,
            "presente/includes/qr_code.html",
            {
                "checkin_url": checkin_url,
                "activity": activity,
                "timeout": activity.qr_timeout,
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


class MyAttendancesView(LoginRequiredMixin, PageTitleMixin, TemplateView):
    """View showing the current user's attendances"""

    template_name = "presente/my_attendances.html"
    page_title = _("Minhas Presenças")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = (
            Attendance.objects.filter(user=self.request.user)
            .select_related("activity", "activity__event")
            .order_by("-checked_in_at")
        )
        return context
