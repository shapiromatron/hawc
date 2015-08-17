from django.core.urlresolvers import reverse

from utils.views import (BaseDetail, BaseDelete,
                         BaseVersion, BaseUpdate, BaseCreate,
                         BaseCreateWithFormset, BaseUpdateWithFormset,
                         CloseIfSuccessMixin, BaseList, GenerateReport)

from assessment.models import Assessment
from study.models import Study

from . import forms, models


# Study criteria
class StudyCriteriaCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Criteria created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Criteria
    form_class = forms.CriteriaForm


# Study population
class StudyPopulationCreate(BaseCreate):
    success_message = 'Study-population created.'
    parent_model = Study
    parent_template_name = 'study'
    model = models.StudyPopulation
    form_class = forms.StudyPopulationForm


class StudyPopulationDetail(BaseDetail):
    model = models.StudyPopulation


class StudyPopulationUpdate(BaseUpdate):
    success_message = "Study Population updated."
    model = models.StudyPopulation
    form_class = forms.StudyPopulationForm


class StudyPopulationDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.StudyPopulation

    def get_success_url(self):
        self.parent = self.object.study
        return reverse("study:detail", kwargs={"pk": self.parent.pk})


# Factors
class AdjustmentFactorCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Adjustment factor created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.AdjustmentFactor
    form_class = forms.AdjustmentFactorForm


# Outcome
class OutcomeCreate(BaseCreate):
    success_message = 'Outcome created.'
    parent_model = models.StudyPopulation
    parent_template_name = 'study_population'
    model = models.Outcome
    form_class = forms.OutcomeForm

    def get_form_kwargs(self):
        kwargs = super(OutcomeCreate, self).get_form_kwargs()
        kwargs['assessment'] = self.assessment
        return kwargs


class OutcomeDetail(BaseDetail):
    model = models.Outcome


class OutcomeUpdate(BaseUpdate):
    success_message = "Outcome updated."
    model = models.Outcome
    form_class = forms.OutcomeForm


class OutcomeDelete(BaseDelete):
    success_message = "Outcome deleted."
    model = models.Outcome

    def get_success_url(self):
        self.parent = self.object.study_population
        return reverse("epi2:sp_detail", kwargs={"pk": self.parent.pk})


# Group collection + group
class GroupCollectionCreate(BaseCreate):
    success_message = 'Group collection created.'
    parent_model = models.StudyPopulation
    parent_template_name = 'study_population'
    model = models.GroupCollection
    form_class = forms.GroupCollection


class GroupCollectionDetail(BaseDetail):
    model = models.GroupCollection


class GroupCollectionUpdate(BaseUpdate):
    success_message = "Group collection updated."
    model = models.GroupCollection
    form_class = forms.GroupCollection


class GroupCollectionDelete(BaseDelete):
    success_message = "Group collection deleted."
    model = models.GroupCollection

    def get_success_url(self):
        self.parent = self.object.study_population
        return reverse("epi2:sp_detail", kwargs={"pk": self.parent.pk})
