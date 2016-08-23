from django.db.models import Q

from assessment.models import Assessment
from study.models import Study
from study.views import StudyRead
from utils.views import (BaseDetail, BaseDelete,
                         BaseUpdate, BaseCreate,
                         BaseCreateWithFormset, BaseUpdateWithFormset,
                         CloseIfSuccessMixin, BaseList)

from . import forms, exports, models


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

    def get_form_kwargs(self):
        kwargs = super(StudyPopulationCreate, self).get_form_kwargs()

        if 'id' in kwargs['initial']:
            # add additional M2M through relationships
            initial = self.model.objects.get(id=kwargs['initial']['id'])
            kwargs['initial']['inclusion_criteria'] = \
                initial.inclusion_criteria.values_list('id', flat=True)
            kwargs['initial']['exclusion_criteria'] = \
                initial.exclusion_criteria.values_list('id', flat=True)
            kwargs['initial']['confounding_criteria'] = \
                initial.confounding_criteria.values_list('id', flat=True)

        return kwargs


class StudyPopulationCopyAsNewSelector(StudyRead):
    template_name = 'epi/studypopulation_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(StudyPopulationCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.StudyPopulationSelectorForm(parent_id=self.object.id)
        return context


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
        return self.object.study.get_absolute_url()


# Factors
class AdjustmentFactorCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Adjustment factor created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.AdjustmentFactor
    form_class = forms.AdjustmentFactorForm


# Exposure
class ExposureCreate(BaseCreate):
    success_message = 'Exposure created.'
    parent_model = models.StudyPopulation
    parent_template_name = 'study_population'
    model = models.Exposure
    form_class = forms.ExposureForm


class ExposureCopyAsNewSelector(StudyPopulationDetail):
    template_name = 'epi/exposure_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(ExposureCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.ExposureSelectorForm(parent_id=self.object.id)
        return context


class ExposureDetail(BaseDetail):
    model = models.Exposure


class ExposureUpdate(BaseUpdate):
    success_message = "Study Population updated."
    model = models.Exposure
    form_class = forms.ExposureForm


class ExposureDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Exposure

    def get_success_url(self):
        return self.object.study_population.get_absolute_url()


# Outcome
class OutcomeList(BaseList):
    parent_model = Assessment
    model = models.Outcome

    def get_paginate_by(self, qs):
        val = 25
        try:
            val = int(self.request.GET.get('paginate_by', val))
        except ValueError:
            pass
        return val

    def get(self, request, *args, **kwargs):
        if len(self.request.GET) > 0:
            self.form = forms.OutcomeFilterForm(
                self.request.GET,
                assessment_id=self.assessment.id
            )
        else:
            self.form = forms.OutcomeFilterForm(
                assessment_id=self.assessment.id
            )
        return super(OutcomeList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        perms = super(OutcomeList, self).get_obj_perms()

        query = Q(assessment=self.assessment)
        order_by = None

        if not perms['edit']:
            query &= Q(study_population__study__published=True)
        if self.form.is_valid():
            query &= self.form.get_query()
            order_by = self.form.get_order_by()

        ids = self.model.objects.filter(query)\
            .distinct('id')\
            .values_list('id', flat=True)

        qs = self.model.objects.filter(id__in=ids)

        if order_by:
            qs = qs.order_by(order_by)

        return qs

    def get_context_data(self, **kwargs):
        context = super(OutcomeList, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['outcome_json'] = self.model.get_qs_json(
            context['object_list'], json_encode=True)
        return context


class OutcomeExport(OutcomeList):
    """
    Full XLS data export for the epidemiology outcome.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        exporter = exports.OutcomeComplete(
            self.object_list,
            export_format="excel",
            filename='{}-epi'.format(self.assessment),
            sheet_name='epi')
        return exporter.build_response()


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


class OutcomeCopyAsNewSelector(StudyPopulationDetail):
    template_name = 'epi/outcome_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(OutcomeCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.OutcomeSelectorForm(parent_id=self.object.id)
        return context


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
        return self.object.study_population.get_absolute_url()


# Result
class ResultCreate(BaseCreateWithFormset):
    success_message = 'Result created.'
    parent_model = models.Outcome
    parent_template_name = 'outcome'
    model = models.Result
    form_class = forms.ResultForm
    formset_factory = forms.GroupResultFormset

    def get_form_kwargs(self):
        kwargs = super(ResultCreate, self).get_form_kwargs()

        if 'id' in kwargs['initial']:
            # add additional M2M through relationships
            initial = self.model.objects.get(id=kwargs['initial']['id'])
            kwargs['initial']['factors_applied'] = \
                initial.factors_applied.values_list('id', flat=True)
            kwargs['initial']['factors_considered'] = \
                initial.factors_considered.values_list('id', flat=True)

        return kwargs

    def post_object_save(self, form, formset):
        for form in formset.forms:
            form.instance.result = self.object

    def get_formset_kwargs(self):
        return {
            "outcome": self.parent,
            "study_population": self.parent.study_population
        }

    def build_initial_formset_factory(self):
        return forms.BlankGroupResultFormset(
            queryset=models.GroupResult.objects.none(),
            **self.get_formset_kwargs())


class ResultCopyAsNewSelector(OutcomeDetail):
    template_name = 'epi/result_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(ResultCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.ResultSelectorForm(parent_id=self.object.id)
        return context


class ResultDetail(BaseDetail):
    model = models.Result


class ResultUpdate(BaseUpdateWithFormset):
    success_message = "Result updated."
    model = models.Result
    form_class = forms.ResultUpdateForm
    formset_factory = forms.GroupResultFormset

    def build_initial_formset_factory(self):
        return forms.GroupResultFormset(
            queryset=self.object.results.all(),
            **self.get_formset_kwargs())

    def get_formset_kwargs(self):
        return {
            "study_population": self.object.outcome.study_population,
            "outcome": self.object.outcome,
            "result": self.object
        }

    def post_object_save(self, form, formset):
        # delete other results not associated with the selected collection
        models.GroupResult.objects\
            .filter(result=self.object)\
            .exclude(group__comparison_set=self.object.comparison_set)\
            .delete()


class ResultDelete(BaseDelete):
    success_message = "Result deleted."
    model = models.Result

    def get_success_url(self):
        return self.object.outcome.get_absolute_url()


# Comparison set + group
class ComparisonSetCreate(BaseCreateWithFormset):
    success_message = 'Groups created.'
    parent_model = models.StudyPopulation
    parent_template_name = 'study_population'
    model = models.ComparisonSet
    form_class = forms.ComparisonSet
    formset_factory = forms.GroupFormset

    def post_object_save(self, form, formset):
        group_id = 0
        for form in formset.forms:
            form.instance.comparison_set = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.group_id = group_id
                if form.has_changed() is False:
                    form.instance.save()  # ensure new group_id saved to db
                group_id += 1

    def build_initial_formset_factory(self):
        return forms.BlankGroupFormset(
            queryset=models.Group.objects.none())


class ComparisonSetOutcomeCreate(ComparisonSetCreate):
    parent_model = models.Outcome
    parent_template_name = 'outcome'


class ComparisonSetStudyPopCopySelector(StudyPopulationDetail):
    template_name = 'epi/comparisonset_sp_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(ComparisonSetStudyPopCopySelector, self).get_context_data(**kwargs)
        context['form'] = forms.ComparisonSetByStudyPopulationSelectorForm(parent_id=self.object.id)
        return context


class ComparisonSetOutcomeCopySelector(OutcomeDetail):
    template_name = 'epi/comparisonset_outcome_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(ComparisonSetOutcomeCopySelector, self).get_context_data(**kwargs)
        context['form'] = forms.ComparisonSetByOutcomeSelectorForm(parent_id=self.object.id)
        return context


class ComparisonSetDetail(BaseDetail):
    model = models.ComparisonSet


class ComparisonSetUpdate(BaseUpdateWithFormset):
    success_message = "Comparison set updated."
    model = models.ComparisonSet
    form_class = forms.ComparisonSet
    formset_factory = forms.GroupFormset

    def build_initial_formset_factory(self):
        # make sure at least one group exists; we check because it's possible
        # to delete as well as create objects in this view.
        qs = self.object.groups.all().order_by('group_id')
        fs = forms.GroupFormset(queryset=qs)
        if qs.count() == 0:
            fs.extra = 1
        return fs

    def post_object_save(self, form, formset):
        group_id = 0
        for form in formset.forms:
            form.instance.comparison_set = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.group_id = group_id
                if form.has_changed() is False:
                    form.instance.save()  # ensure new group_id saved to db
                group_id += 1


class ComparisonSetDelete(BaseDelete):
    success_message = "Comparison set deleted."
    model = models.ComparisonSet

    def get_success_url(self):
        if self.object.study_population:
            return self.object.study_population.get_absolute_url()
        else:
            return self.object.outcome.get_absolute_url()


class GroupDetail(BaseDetail):
    model = models.Group


class GroupUpdate(BaseUpdateWithFormset):
    success_message = "Groups updated."
    model = models.Group
    form_class = forms.SingleGroupForm
    formset_factory = forms.GroupNumericalDescriptionsFormset

    def build_initial_formset_factory(self):
        return forms.GroupNumericalDescriptionsFormset(
            queryset=self.object.descriptions.all())

    def post_object_save(self, form, formset):
        for form in formset:
            form.instance.group = self.object
