from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

User = get_user_model()


class Activity(models.Model):
    owners = models.ManyToManyField(
        User,
        related_name="owned_activities",
        verbose_name=_("Responsáveis"),
        blank=True,
    )
    title = models.CharField(_("Título"), max_length=100)
    tags = TaggableManager(
        verbose_name=_("Tags"),
        help_text=_(
            "Tags para organizar as atividades (ex: 'Workshop 2024', 'Python')"
        ),
        blank=True,
    )
    start_time = models.DateTimeField(_("Data/hora de início"))
    end_time = models.DateTimeField(_("Data/hora de término"))
    is_published = models.BooleanField(
        _("Publicado"),
        default=False,
        help_text=_("Define se a atividade está visível para registro de presença"),
    )
    qr_timeout = models.IntegerField(
        _("Timeout do QR Code (segundos)"),
        default=30,
        help_text=_(
            "Tempo de validade de cada QR Code para registro de presença (em segundos)"
        ),
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
        verbose_name=_("Atividade"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Usuário"),
    )
    checked_in_at = models.DateTimeField(_("Registrado em"), auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.activity}"

    class Meta:
        verbose_name = _("Presença")
        verbose_name_plural = _("Presenças")
        unique_together = [["activity", "user"]]
        ordering = ["-checked_in_at"]
