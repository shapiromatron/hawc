from django.urls import reverse
from django.views.generic.edit import CreateView

from hawc.apps.common.views import LoginRequiredMixin, MessageMixin

from .forms import UDFForm


class CreateUDFView(LoginRequiredMixin, MessageMixin, CreateView):
    template_name = "udf/udf_form.html"
    form_class = UDFForm
    success_message = "Form created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self) -> str:
        return reverse("portal")
