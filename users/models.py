from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import unicodedata


class User(AbstractUser):
    class UserType(models.TextChoices):
        SERVIDOR = "SERVIDOR", _("Servidor")
        ALUNO = "ALUNO", _("Aluno")

    email = models.EmailField(_("E-mail"), unique=True)
    username = models.CharField(
        _("Nome de usuário"), max_length=150, blank=True, null=True
    )
    full_name = models.CharField(
        _("Nome completo"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Nome completo do usuário (usa nome social se disponível)"),
    )
    full_name_normalized = models.CharField(
        _("Nome normalizado"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Nome sem acentos para ordenação"),
        db_index=True,
    )
    type = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=UserType.choices,
        blank=True,
        null=True,
    )
    avatar_url = models.URLField(
        _("URL do avatar"),
        max_length=500,
        blank=True,
        null=True,
    )
    is_suap_user = models.BooleanField(
        _("Usuário SUAP"),
        default=False,
        help_text=_("Indica se o usuário foi criado via login SUAP"),
    )
    curso = models.CharField(
        _("Curso"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Curso do aluno (apenas para tipo ALUNO)"),
    )
    periodo_referencia = models.CharField(
        _("Período"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Período de referência do aluno (apenas para tipo ALUNO)"),
    )
    campus = models.CharField(
        _("Campus"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Campus do usuário no IFRN"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        # Normalize full_name for sorting (remove accents and normalize case)
        if self.full_name:
            # NFD = Canonical Decomposition (separates base chars from accents)
            nfd = unicodedata.normalize("NFD", self.full_name)
            # Filter out combining characters (accents) and convert to uppercase
            self.full_name_normalized = "".join(
                char for char in nfd if unicodedata.category(char) != "Mn"
            ).upper()
        else:
            self.full_name_normalized = None

        super().save(*args, **kwargs)

    @property
    def matricula(self):
        if self.is_suap_user:
            social_account = self.socialaccount_set.filter(provider="suap").first()
            if social_account:
                return social_account.uid
        return None

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def __str__(self):
        return self.get_full_name()
