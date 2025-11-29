from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from taggit.managers import TaggableManager

User = get_user_model()


class Network(models.Model):
    name = models.CharField(
        _("Nome"),
        max_length=100,
        unique=True,
        help_text=_("Nome identificador da rede (ex: 'Campus Natal Central')"),
    )
    description = models.TextField(
        _("Descrição"),
        blank=True,
        help_text=_("Descrição opcional da rede"),
    )
    ip_addresses = models.TextField(
        _("Endereços IP/Redes"),
        help_text=_(
            "IPs ou redes permitidas (um por linha). "
            "Exemplo: 192.168.1.0/24 ou 10.0.0.1"
        ),
    )
    is_active = models.BooleanField(
        _("Ativo"),
        default=True,
        help_text=_("Desmarque para desativar temporariamente esta rede"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Rede")
        verbose_name_plural = _("Redes")
        ordering = ["name"]


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
    allowed_networks = models.ManyToManyField(
        Network,
        verbose_name=_("Redes permitidas"),
        blank=True,
        help_text=_("Selecione as redes que podem acessar esta atividade"),
    )

    def __str__(self):
        return self.title

    def is_expired(self):
        return timezone.now() > self.end_time

    def is_not_started(self):
        return timezone.now() < self.start_time

    def is_ip_allowed(self, client_ip):
        import logging

        logger = logging.getLogger(__name__)

        # If IP restriction is disabled, allow all
        if not self.restrict_ip:
            logger.debug(
                f"IP restriction disabled for activity {self.id}, allowing {client_ip}"
            )
            return True

        # Get active networks for this activity
        active_networks = self.allowed_networks.filter(is_active=True)

        # If no networks configured, deny all (when restriction is enabled)
        if not active_networks.exists():
            logger.warning(
                f"IP restriction enabled but no active networks configured for activity {self.id}, denying {client_ip}"
            )
            return False

        from ipaddress import ip_address, ip_network

        try:
            client_addr = ip_address(client_ip)
            logger.debug(f"Checking IP {client_ip} for activity {self.id}")

            # Check against each configured network
            for network_config in active_networks:
                logger.debug(f"Checking against network: {network_config.name}")

                # Parse IP addresses from the network config (one per line)
                ip_list = [
                    ip.strip()
                    for ip in network_config.ip_addresses.split("\n")
                    if ip.strip()
                ]

                for ip_entry in ip_list:
                    try:
                        # Try to match as network (CIDR notation)
                        if "/" in ip_entry:
                            network_obj = ip_network(ip_entry, strict=False)
                            if client_addr in network_obj:
                                logger.info(
                                    f"IP {client_ip} matched network {ip_entry} in {network_config.name} for activity {self.id}"
                                )
                                return True
                        # Match as individual IP
                        else:
                            ip_addr = ip_address(ip_entry)
                            if client_addr == ip_addr:
                                logger.info(
                                    f"IP {client_ip} matched individual IP {ip_entry} in {network_config.name} for activity {self.id}"
                                )
                                return True
                    except ValueError as e:
                        # Invalid IP configuration, skip
                        logger.error(
                            f"Invalid IP '{ip_entry}' in network {network_config.name}: {e}"
                        )
                        continue

            logger.warning(
                f"IP {client_ip} denied access to activity {self.id} - no matching networks"
            )
            return False
        except ValueError as e:
            # Invalid client IP, deny access
            logger.error(f"Invalid client IP '{client_ip}': {e}")
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
    ip_address = models.GenericIPAddressField(
        _("Endereço IP"),
        blank=True,
        null=True,
        help_text=_("Endereço IP do usuário no momento do check-in"),
    )

    def __str__(self):
        return f"{self.user} - {self.activity}"

    def get_network_name(self):
        if not self.ip_address:
            return "-"

        from ipaddress import ip_address, ip_network

        try:
            client_addr = ip_address(self.ip_address)

            # Check all active networks
            for network_config in Network.objects.filter(is_active=True):
                ip_list = [
                    ip.strip()
                    for ip in network_config.ip_addresses.split("\n")
                    if ip.strip()
                ]

                for ip_entry in ip_list:
                    try:
                        # Try to match as network (CIDR notation)
                        if "/" in ip_entry:
                            network_obj = ip_network(ip_entry, strict=False)
                            if client_addr in network_obj:
                                return network_config.name
                        # Match as individual IP
                        else:
                            ip_addr = ip_address(ip_entry)
                            if client_addr == ip_addr:
                                return network_config.name
                    except ValueError:
                        # Invalid IP configuration, skip
                        continue

            # No network matched, return the IP address
            return self.ip_address
        except ValueError:
            # Invalid IP address
            return self.ip_address

    class Meta:
        verbose_name = _("Presença")
        verbose_name_plural = _("Presenças")
        unique_together = [["activity", "user"]]
        ordering = ["-checked_in_at"]
