from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from presente.tables import CoreTable
from .models import User


class UserTable(CoreTable):
    full_name = tables.Column(verbose_name=_("Nome"), empty_values=())

    def render_full_name(self, record):
        return f"{record.first_name} {record.last_name}"

    class Meta:
        model = User
        fields = ("full_name", "email", "groups", "last_login")


class GroupTable(CoreTable):
    class Meta:
        model = Group
        fields = [
            "name",
        ]
