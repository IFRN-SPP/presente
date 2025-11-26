from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Event(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_events",
        verbose_name=_("owner"),
        null=True,
        blank=True,
    )
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"))
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventos")


class Activity(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_activities",
        verbose_name=_("owner"),
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activities",
        verbose_name=_("event"),
    )
    title = models.CharField(_("title"), max_length=100)
    start_time = models.DateTimeField(_("start time"))
    end_time = models.DateTimeField(_("end time"))
    is_published = models.BooleanField(default=False)
    qr_timeout = models.IntegerField(
        _("QR code timeout (seconds)"),
        default=30,
        help_text=_("How long each QR code is valid for check-in (in seconds)"),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Atividade")
        verbose_name_plural = _("Atividades")


class Attendance(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("activity"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("user"),
    )
    checked_in_at = models.DateTimeField(_("checked in at"), auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.activity}"

    class Meta:
        verbose_name = _("Presença")
        verbose_name_plural = _("Presenças")
        unique_together = [["activity", "user"]]
        ordering = ["-checked_in_at"]
