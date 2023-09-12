from django.urls import reverse
from django.views.generic.edit import CreateView

from hawc.apps.common.views import LoginRequiredMixin

from .forms import UDFForm


class CreateUDFView(LoginRequiredMixin, CreateView):
    template_name = "form_library/udf_form.html"
    form_class = UDFForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self) -> str:
        return reverse("portal")
