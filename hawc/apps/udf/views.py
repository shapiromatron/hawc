from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView

from hawc.apps.common import dynamic_forms
from hawc.apps.common.views import LoginRequiredMixin, MessageMixin, htmx_required, BaseCreate

from . import models
from .forms import SchemaPreviewForm, UDFForm


# UDF views
class UDFListView(LoginRequiredMixin, ListView):
    template_name = "udf/udf_list.html"
    model = models.UserDefinedForm


class UDFDetailView(LoginRequiredMixin, DetailView):
    template_name = "udf/udf_detail.html"
    model = models.UserDefinedForm

    def get_context_data(self, **kwargs):
        form = dynamic_forms.Schema.parse_obj(self.object.schema).to_form()
        kwargs.update(form=form)
        return super().get_context_data(**kwargs)

    def user_can_edit(self):
        return self.object.user_can_edit(self.request.user)


class CreateUDFView(LoginRequiredMixin, MessageMixin, CreateView):
    template_name = "udf/udf_form.html"
    form_class = UDFForm
    success_url = reverse_lazy("udf:udf_list")
    success_message = "Form created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self) -> str:
        return reverse_lazy("portal")


class UpdateUDFView(LoginRequiredMixin, MessageMixin, UpdateView):
    template_name = "udf/udf_form.html"
    form_class = UDFForm
    model = models.UserDefinedForm
    success_url = reverse_lazy("udf:udf_list")
    success_message = "Form updated."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs


@method_decorator(htmx_required, name="dispatch")
class SchemaPreview(LoginRequiredMixin, FormView):
    """Custom form schema preview view. Utilizes HTMX."""

    template_name = "udf/schema_preview.html"

    form_class = SchemaPreviewForm
    http_method_names = ["post"]
    field_name = "schema"

    def get_form_kwargs(self):
        """Get form keyword arguments (the schema)."""
        return {"data": {"schema": self.request.POST.get(self.field_name)}}

    def get_context_data(self, **kwargs):
        """Get context data used in the template. Add field and modal ID."""
        kwargs.update(field=self.field_name, modal_id=f"{self.field_name}-preview")
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """Process a valid dynamic form/schema."""
        dynamic_form = dynamic_forms.Schema.parse_obj(form.cleaned_data["schema"]).to_form(
            prefix=self.field_name
        )
        return self.render_to_response(self.get_context_data(valid=True, form=dynamic_form))

    def form_invalid(self, form):
        """Process invalid dynamic form/schema."""
        return self.render_to_response(self.get_context_data(valid=False))


# Model binding views
class CreateModelBindingView(BaseCreate):
