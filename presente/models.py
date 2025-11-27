from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

User = get_user_model()


class Activity(models.Model):
    owners = models.ManyToManyField(
        User,
        related_name="owned_activities",
        verbose_name=_("owners"),
        blank=True,
    )
    title = models.CharField(_("title"), max_length=100)
    tags = TaggableManager(
        verbose_name=_("tags"),
        help_text=_(
            "Tags para organizar as atividades (ex: 'Workshop 2024', 'Python')"
        ),
        blank=True,
    )
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
