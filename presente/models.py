from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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
    restrict_ip = models.BooleanField(
        _("Restringir por IP"),
        default=False,
        help_text=_("Ativar restrição de acesso por endereço IP"),
    )
    allowed_networks = models.TextField(
        _("Redes permitidas"),
        blank=True,
        null=True,
        help_text=_(
            "IPs ou redes permitidas (um por linha). "
            "Exemplo: 192.168.1.0/24 ou 10.0.0.1"
        ),
    )

    def __str__(self):
        return self.title

    def is_expired(self):
        """Check if the activity has ended (past end_time)"""
        return timezone.now() > self.end_time

    def is_not_started(self):
        """Check if the activity hasn't started yet (before start_time)"""
        return timezone.now() < self.start_time

    def is_ip_allowed(self, client_ip):
        """Check if client IP is allowed to access this activity"""
        # If IP restriction is disabled, allow all
        if not self.restrict_ip:
            return True

        # If no networks configured, deny all (when restriction is enabled)
        if not self.allowed_networks:
            return False

        from ipaddress import ip_address, ip_network

        try:
            client_addr = ip_address(client_ip)

            # Parse allowed networks (one per line)
            networks = [
                n.strip() for n in self.allowed_networks.split("\n") if n.strip()
            ]

            for network in networks:
                try:
                    # Try to match as network (CIDR notation)
                    if "/" in network:
                        if client_addr in ip_network(network, strict=False):
                            return True
                    # Match as individual IP
                    else:
                        if client_addr == ip_address(network):
                            return True
                except ValueError:
                    # Invalid network configuration, skip
                    continue

            return False
        except ValueError:
            # Invalid client IP, deny access
            return False

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
