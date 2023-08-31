from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, FormView

from hawc.apps.common import dynamic_forms
from hawc.apps.common.views import LoginRequiredMixin, htmx_required

from .forms import CustomDataExtractionForm, SchemaPreviewForm


class CreateDataExtractionView(LoginRequiredMixin, CreateView):
    template_name = "form_library/custom_data_extraction_form.html"
    form_class = CustomDataExtractionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self) -> str:
        return reverse("portal")


@method_decorator(htmx_required, name="dispatch")
class SchemaPreview(LoginRequiredMixin, FormView):
    """Custom form schema preview view. Utilizes HTMX."""

    template_name = "form_library/schema_modal.html"

    form_class = SchemaPreviewForm
    http_method_names = ["post"]

    def get_form_kwargs(self):
        """Get form keyword arguments (the schema)."""
        return {"data": {"schema": self.request.POST.get(self.kwargs["field"])}}

    def get_context_data(self, **kwargs):
        """Get context data used in the template. Add field and modal ID."""
        kwargs.update(field=self.kwargs["field"], modal_id=f'{self.kwargs["field"]}-preview')
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """Process a valid dynamic form/schema."""
        dynamic_form = dynamic_forms.Schema.parse_obj(form.cleaned_data["schema"]).to_form(
            prefix=self.kwargs["field"]
        )
        return self.render_to_response(self.get_context_data(valid=True, form=dynamic_form))

    def form_invalid(self, form):
        """Process invalid dynamic form/schema."""
        return self.render_to_response(self.get_context_data(valid=False))
