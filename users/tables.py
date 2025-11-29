from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from presente.tables import CoreTable
from .models import User


class UserTable(CoreTable):
    full_name = tables.Column(verbose_name=_("Nome"), empty_values=())
    matricula = tables.Column(verbose_name=_("Matrícula"), empty_values=())
    type = tables.Column(verbose_name=_("Tipo"), empty_values=())
    campus = tables.Column(verbose_name=_("Campus"), empty_values=())
    curso = tables.Column(verbose_name=_("Curso"), empty_values=())
    periodo_referencia = tables.Column(verbose_name=_("Período"), empty_values=())

    def render_full_name(self, record):
        # Use full_name field if available, otherwise fallback to first_name + last_name
        if record.full_name:
            return record.full_name
        return f"{record.first_name} {record.last_name}".strip() or "-"

    def render_matricula(self, record):
        return record.matricula or "-"

    def render_type(self, record):
        if record.type:
            return record.get_type_display()
        return "-"

    def render_campus(self, record):
        return record.campus or "-"

    def render_curso(self, record):
        return record.curso or "-"

    def render_periodo_referencia(self, record):
        return record.periodo_referencia or "-"

    class Meta:
        model = User
        fields = (
            "full_name",
            "matricula",
            "type",
            "campus",
            "curso",
            "periodo_referencia",
            "last_login",
        )
