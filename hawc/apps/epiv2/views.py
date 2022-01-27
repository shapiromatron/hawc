from ..common.views import BaseCreate, BaseDetail, BaseUpdate
from ..study.models import Study
from . import forms, models


# Design (Study Population)
class DesignCreate(BaseCreate):
    success_message = "Study-population created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm


class DesignUpdate(BaseUpdate):
    success_message = "Study-population updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm


class DesignDetail(BaseDetail):
    model = models.Design
