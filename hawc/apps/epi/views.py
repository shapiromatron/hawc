from ..assessment.models import Assessment
from ..common.views import (
    BaseCopyForm,
    BaseCreate,
    BaseCreateWithFormset,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseUpdate,
    BaseUpdateWithFormset,
    CloseIfSuccessMixin,
    HeatmapBase,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from . import filterset, forms, models


# Heatmap views
class HeatmapStudyDesign(HeatmapBase):
    heatmap_data_class = "epidemiology-study-design"
    heatmap_data_url = "epi:api:assessment-study-heatmap"
    heatmap_view_title = "Epidemiology study design summary"


class HeatmapResults(HeatmapBase):
    heatmap_data_class = "epidemiology-result-summary"
    heatmap_data_url = "epi:api:assessment-result-heatmap"
    heatmap_view_title = "Epidemiology result summary"


# Study criteria
class StudyCriteriaCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = "Criteria created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.Criteria
    form_class = forms.CriteriaForm


# Study population
class StudyPopulationCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Study-population created."
    parent_model = Study
    parent_template_name = "study"
    model = models.StudyPopulation
    form_class = forms.StudyPopulationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if "id" in kwargs["initial"]:
            # add additional M2M through relationships
            initial = self.model.objects.get(id=kwargs["initial"]["id"])
            kwargs["initial"]["inclusion_criteria"] = initial.inclusion_criteria.values_list(
                "id", flat=True
            )
            kwargs["initial"]["exclusion_criteria"] = initial.exclusion_criteria.values_list(
                "id", flat=True
            )
            kwargs["initial"]["confounding_criteria"] = initial.confounding_criteria.values_list(
                "id", flat=True
            )

        return kwargs


class StudyPopulationCopyForm(BaseCopyForm):
    copy_model = models.StudyPopulation
    form_class = forms.StudyPopulationSelectorForm
    model = Study


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
    success_message = "Adjustment factor created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.AdjustmentFactor
    form_class = forms.AdjustmentFactorForm


# Exposure
class ExposureCreate(BaseCreateWithFormset):
    success_message = "Exposure created."
    parent_model = models.StudyPopulation
    parent_template_name = "study_population"
    model = models.Exposure
    form_class = forms.ExposureForm
    formset_factory = forms.CentralTendencyFormset

    def post_object_save(self, form, formset):
        # need to get the exposure_id to save the central tendency objects
        for form in formset.forms:
            form.instance.exposure = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.exposure_id = self.object.id
                if form.has_changed() is False:
                    # ensure new exposure_id saved to db
                    form.instance.save()

    def build_initial_formset_factory(self):
        return forms.BlankCentralTendencyFormset(queryset=models.CentralTendency.objects.none())


class ExposureCopyForm(BaseCopyForm):
    copy_model = models.Exposure
    form_class = forms.ExposureSelectorForm
    model = models.StudyPopulation


class ExposureDetail(BaseDetail):
    model = models.Exposure


class ExposureUpdate(BaseUpdateWithFormset):
    success_message = "Study Population updated."
    model = models.Exposure
    form_class = forms.ExposureForm
    formset_factory = forms.CentralTendencyFormset

    def build_initial_formset_factory(self):
        # make sure at least one CT exists; we check because it's possible
        # to delete as well as create objects in this view.
        qs = self.object.central_tendencies.all().order_by("id")
        fs = forms.CentralTendencyFormset(queryset=qs)
        if qs.count() == 0:
            fs.extra = 1
        return fs

    def post_object_save(self, form, formset):
        # need to get the exposure_id to save the central tendency objects
        for form in formset.forms:
            form.instance.exposure = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.exposure_id = self.object.id
                if form.has_changed() is False:
                    # ensure new exposure_id saved to db
                    form.instance.save()


class ExposureDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Exposure

    def get_success_url(self):
        return self.object.study_population.get_absolute_url()


# Outcome
class OutcomeFilterList(BaseFilterList):
    parent_model = Assessment
    model = models.Outcome
    filterset_class = filterset.OutcomeFilterSet

    def get_queryset(self):
        return super().get_queryset().select_related("study_population__study")


class OutcomeCreate(BaseCreate):
    success_message = "Outcome created."
    parent_model = models.StudyPopulation
    parent_template_name = "study_population"
    model = models.Outcome
    form_class = forms.OutcomeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs


class OutcomeCopyForm(BaseCopyForm):
    copy_model = models.Outcome
    form_class = forms.OutcomeSelectorForm
    model = models.StudyPopulation


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
    success_message = "Result created."
    parent_model = models.Outcome
    parent_template_name = "outcome"
    model = models.Result
    form_class = forms.ResultForm
    formset_factory = forms.GroupResultFormset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if "id" in kwargs["initial"]:
            # add additional M2M through relationships
            initial = self.model.objects.get(id=kwargs["initial"]["id"])
            kwargs["initial"]["factors_applied"] = initial.factors_applied.values_list(
                "id", flat=True
            )
            kwargs["initial"]["factors_considered"] = initial.factors_considered.values_list(
                "id", flat=True
            )

        return kwargs

    def post_object_save(self, form, formset):
        for form in formset.forms:
            form.instance.result = self.object

    def get_formset_kwargs(self):
        return {
            "outcome": self.parent,
            "study_population": self.parent.study_population,
        }

    def build_initial_formset_factory(self):
        return forms.BlankGroupResultFormset(
            queryset=models.GroupResult.objects.none(), **self.get_formset_kwargs()
        )


class ResultCopyForm(BaseCopyForm):
    copy_model = models.Result
    form_class = forms.ResultSelectorForm
    model = models.Outcome


class ResultDetail(BaseDetail):
    model = models.Result


class ResultUpdate(BaseUpdateWithFormset):
    success_message = "Result updated."
    model = models.Result
    form_class = forms.ResultUpdateForm
    formset_factory = forms.GroupResultFormset

    def build_initial_formset_factory(self):
        return forms.GroupResultFormset(
            queryset=self.object.results.all(), **self.get_formset_kwargs()
        )

    def get_formset_kwargs(self):
        return {
            "study_population": self.object.outcome.study_population,
            "outcome": self.object.outcome,
            "result": self.object,
        }

    def post_object_save(self, form, formset):
        # delete other results not associated with the selected collection
        models.GroupResult.objects.filter(result=self.object).exclude(
            group__comparison_set=self.object.comparison_set
        ).delete()


class ResultDelete(BaseDelete):
    success_message = "Result deleted."
    model = models.Result

    def get_success_url(self):
        return self.object.outcome.get_absolute_url()


# Comparison set + group
class ComparisonSetCreate(BaseCreateWithFormset):
    success_message = "Groups created."
    parent_model = models.StudyPopulation
    parent_template_name = "study_population"
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
        return forms.BlankGroupFormset(queryset=models.Group.objects.none())


class ComparisonSetOutcomeCreate(ComparisonSetCreate):
    parent_model = models.Outcome
    parent_template_name = "outcome"


class ComparisonSetStudyPopCopySelector(BaseCopyForm):
    copy_model = models.ComparisonSet
    form_class = forms.ComparisonSetByStudyPopulationSelectorForm
    model = models.StudyPopulation


class ComparisonSetOutcomeCopySelector(BaseCopyForm):
    copy_model = models.ComparisonSet
    form_class = forms.ComparisonSetByOutcomeSelectorForm
    model = models.Outcome


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
        qs = self.object.groups.all().order_by("group_id")
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
        return forms.GroupNumericalDescriptionsFormset(queryset=self.object.descriptions.all())

    def post_object_save(self, form, formset):
        for form in formset:
            form.instance.group = self.object
