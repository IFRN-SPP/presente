from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class User(AbstractUser):
    class UserType(models.TextChoices):
        SERVIDOR = "SERVIDOR", _("Servidor")
        ALUNO = "ALUNO", _("Aluno")

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=150, blank=True, null=True)
    type = models.CharField(
        _("tipo"),
        max_length=20,
        choices=UserType.choices,
        blank=True,
        null=True,
    )
    avatar_url = models.URLField(
        _("avatar URL"),
        max_length=500,
        blank=True,
        null=True,
    )
    is_suap_user = models.BooleanField(
        _("usuário SUAP"),
        default=False,
        help_text=_("Indica se o usuário foi criado via login SUAP"),
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
        super().save(*args, **kwargs)

    def __str__(self):
        if self.first_name:
            return self.first_name
        else:
            return self.email
