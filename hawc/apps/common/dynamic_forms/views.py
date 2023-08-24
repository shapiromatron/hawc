from forms import CustomDataExtractionForm

from hawc.apps.common import views


class CreateDataExtractionView(views.BaseCreate):
    form_class = CustomDataExtractionForm
