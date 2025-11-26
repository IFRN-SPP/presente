from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django_tables2 import SingleTableMixin
from .mixins import (
    CoreBaseMixin,
    CoreBaseEditMixin,
)


class CoreListView(
    CoreBaseMixin,
    SingleTableMixin,
    ListView,
):
    template_name = "core/list.html"
    permission_action = "view"


class CoreDetailView(
    CoreBaseMixin,
    DetailView,
):
    template_name = "core/detail.html"
    permission_action = "view"
    page_title = _("Detalhar")
    fields = "__all__"
    safe_fields = ["description", "presentation"]

    def get_fields(self):
        selected_fields = []
        no_check = not isinstance(self.fields, (list, tuple))
        for field in self.object._meta.fields:
            if no_check or field.name in self.fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(self.object, field.name),
                        "safe": True if field.name in self.safe_fields else False,
                    }
                )
        return selected_fields

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fields"] = self.get_fields()
        return context


class CoreCreateView(CoreBaseEditMixin, CreateView):
    template_name = "core/create.html"
    permission_action = "add"


class CoreUpdateView(CoreBaseEditMixin, UpdateView):
    template_name = "core/update.html"
    permission_action = "change"


class CoreDeleteView(CoreBaseEditMixin, DeleteView):
    page_title = _("Remover")
    template_name = "core/delete.html"
    template_name_modal = "core/includes/delete_modal.html"
    permission_action = "delete"

    def get_template_names(self):
        if not self.request.htmx:
            return [self.template_name]
        return [self.template_name_modal]
