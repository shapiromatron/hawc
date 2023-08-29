from django.views.generic.edit import CreateView

from .forms import CustomDataExtractionForm


class CreateDataExtractionView(CreateView):
    template_name = "form_library/custom_data_extraction_form.html"
    form_class = CustomDataExtractionForm
