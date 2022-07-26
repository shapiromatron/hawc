from hawc.apps.assessment.models import Assessment
from hawc.apps.assessmentvalues.forms import AssessmentValuesForm
from hawc.apps.assessmentvalues.models import AssessmentValues
from hawc.apps.common.views import BaseCreate, BaseDelete, BaseDetail, BaseUpdate


class AssessmentValuesCreate(BaseCreate):
    model = AssessmentValues
    parent_model = Assessment
    form_class = AssessmentValuesForm

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


class AssessmentValuesUpdate(BaseUpdate):
    model = AssessmentValues
    parent_model = Assessment
    form_class = AssessmentValuesForm

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()


class AssessmentValuesDetail(BaseDetail):
    model = AssessmentValues


class AssessmentValuesDelete(BaseDelete):
    model = AssessmentValues

    def get_success_url(self):
        return self.object.assessment.get_absolute_url()
