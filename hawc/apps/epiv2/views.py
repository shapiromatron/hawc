from ..common.views import BaseCreate, BaseDelete, BaseDetail, BaseUpdate
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


class DesignDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Design

    def get_success_url(self):
        return self.object.study.get_absolute_url()
