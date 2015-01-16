from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponse

from assessment.models import Assessment
from utils.views import (BaseDetail, BaseDelete,
                         BaseVersion, BaseUpdate, BaseCreate,
                         BaseCreateWithFormset, BaseUpdateWithFormset,
                         CloseIfSuccessMixin, BaseList, GenerateReport)

from study.models import Study
from study.views import StudyRead

from . import forms, models, exports


# Study-level
class EpiStudyList(BaseList):
    parent_model = Assessment
    model = Study
    template_name = 'epi/epistudy_list.html'

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment, study_type=1)


# Study populations
class StudyPopulationCreate(BaseCreate):
    success_message = 'Study-population created.'
    parent_model = Study
    parent_template_name = 'study'
    model = models.StudyPopulation
    form_class = forms.StudyPopulationForm

    def get_form_kwargs(self):
        kwargs = super(StudyPopulationCreate, self).get_form_kwargs()

        # check if we have an object-template to be used
        initial_pk = self.request.GET.get('initial', -1)
        initial = self.model.objects.filter(pk=initial_pk).first()
        if initial and initial.get_assessment() == self.assessment:
            kwargs['instance'] = initial

        return kwargs


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


class StudyPopulationJSON(BaseDetail):
    model = models.StudyPopulation
    http_method_names = ('get', )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(json_encode=True),
                            content_type="application/json")


class StudyPopulationCopyAsNewSelector(StudyRead):
    # Select an existing assessed outcome as a template for a new one
    template_name = 'epi/studypopulation_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(StudyPopulationCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.StudyPopulationSelectorForm()
        return context


# Exposures
class ExposureCreate(BaseCreateWithFormset):
    success_message = 'Exposure created.'
    parent_model = models.StudyPopulation
    parent_template_name = 'study_population'
    model = models.Exposure
    form_class = forms.ExposureForm
    formset_factory = forms.EGFormSet

    def get_form_kwargs(self):
        kwargs = super(ExposureCreate, self).get_form_kwargs()

        # check if we have an object-template to be used
        initial_pk = self.request.GET.get('initial', -1)
        initial = self.model.objects.filter(pk=initial_pk).first()
        if initial and initial.get_assessment() == self.assessment:
            kwargs['instance'] = initial

        return kwargs

    def post_object_save(self, form, formset):
        # Bind newly created exposure to exposure-group instance
        for i, form in enumerate(formset.forms):
            form.instance.exposure_group_id = i
            form.instance.exposure = self.object

    def build_initial_formset_factory(self):
        return forms.BlankEGFormSet(queryset=models.ExposureGroup.objects.none())


class ExposureDetail(BaseDetail):
    model = models.Exposure


class ExposureDelete(BaseDelete):
    success_message = "Exposure deleted."
    model = models.Exposure

    def get_success_url(self):
        self.parent = self.object.study_population
        return reverse("epi:sp_detail", kwargs={"pk": self.parent.pk})


class ExposureUpdate(BaseUpdateWithFormset):
    success_message = "Exposure updated."
    model = models.Exposure
    form_class = forms.ExposureForm
    formset_factory = forms.EGFormSet

    def build_initial_formset_factory(self):
        return forms.EGFormSet(queryset=self.object.groups.all()\
                    .order_by('exposure_group_id'))

    def post_object_save(self, form, formset):
        for form in formset:
            form.instance.exposure = self.object

    def post_formset_save(self, form, formset):
        formset.rebuild_exposure_group_id()


class ExposureCopyAsNewSelector(StudyPopulationDetail):
    # Select an existing assessed outcome as a template for a new one
    template_name = 'epi/exposure_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(ExposureCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.ExposureSelectorForm()
        return context


# Study criteria
class StudyCriteriaCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Epidemiology study-population criteria created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.StudyCriteria
    form_class = forms.StudyCriteriaForm


#Factors
class FactorCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Factor created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Factor
    form_class = forms.FactorForm


# Assessed outcomes
class AssessedOutcomeCreate(BaseCreateWithFormset):
    success_message = 'Assessed-outcome created.'
    parent_model = models.Exposure
    parent_template_name = 'object'
    model = models.AssessedOutcome
    form_class = forms.AssessedOutcomeForm
    formset_factory = forms.AOGFormSet

    def get_form_kwargs(self):
        # bind to assessment
        kwargs = super(AssessedOutcomeCreate, self).get_form_kwargs()
        kwargs['assessment'] = self.assessment

        # check if we have an object-template to be used
        initial_pk = self.request.GET.get('initial', -1)
        initial = self.model.objects.filter(pk=initial_pk).first()
        if initial and initial.get_assessment() == self.assessment:
            kwargs['instance'] = initial

        return kwargs

    def post_object_save(self, form, formset):
        # Bind newly created assessment outcome to assessment group instances
        for form in formset.forms:
            form.instance.assessed_outcome = self.object

    def build_initial_formset_factory(self):
        initial = self.parent.groups.all().order_by('exposure_group_id').values('pk')
        for v in initial:
            v['exposure_group'] = v.pop('pk')
        AOGFormset = modelformset_factory(models.AssessedOutcomeGroup,
                                          form=forms.AOGForm,
                                          extra=len(initial))
        return AOGFormset(queryset=models.AssessedOutcomeGroup.objects.none(),
                          initial=initial)


class AssessedOutcomeDetail(BaseDetail):
    model = models.AssessedOutcome


class AssessedOutcomeVersions(BaseVersion):
    model = models.AssessedOutcome
    template_name = "epi/assessedoutcome_versions.html"


class AssessedOutcomeUpdate(BaseUpdateWithFormset):
    success_message = "Assessment Outcome updated."
    model = models.AssessedOutcome
    form_class = forms.AssessedOutcomeForm
    formset_factory = forms.AOGFormSet

    def build_initial_formset_factory(self):
        return forms.AOGFormSet(queryset=self.object.groups.all() \
                    .order_by('exposure_group__exposure_group_id'))


class AssessedOutcomeDelete(BaseDelete):
    success_message = "Assessment Outcome deleted."
    model = models.AssessedOutcome

    def get_success_url(self):
        self.parent = self.object.exposure
        return reverse("epi:exposure_detail", kwargs={"pk": self.parent.pk})


class AssessedOutcomeFlat(BaseList):
    parent_model = Assessment
    model = models.AssessedOutcome
    crud = "Read"

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(AssessedOutcomeFlat, self).get_obj_perms()
        if not perms['edit']:
            filters["exposure__study_population__study__published"] = True
        return self.model.objects.filter(**filters)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        export_format = request.GET.get("output", "excel")
        exporter = exports.AssessedOutcomeFlatDataPivot(
                self.object_list,
                export_format=export_format,
                filename='{}-epi'.format(self.assessment))
        return exporter.build_response()


class AssessedOutcomeReport(GenerateReport):
    parent_model = Assessment
    model = models.AssessedOutcome
    report_type = 3

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(AssessedOutcomeReport, self).get_obj_perms()
        if not perms['edit']:
            filters["exposure__study_population__study__published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "epidemiology.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class FullExport(AssessedOutcomeFlat):
    """
    Full XLS data export for the epidemiology outcome.
    """
    parent_model = Assessment
    model = models.AssessedOutcome
    crud = "Read"

    def get(self, request, *args, **kwargs):
        self.object_list = super(FullExport, self).get_queryset()
        exporter = exports.AssessedOutcomeFlatComplete(
                self.object_list,
                export_format="excel",
                filename='{}-epi'.format(self.assessment),
                sheet_name='epi')
        return exporter.build_response()


class AssessedOutcomeCopyAsNewSelector(ExposureDetail):
    # Select an existing assessed outcome as a template for a new one
    template_name = 'epi/assessedoutcome_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(AssessedOutcomeCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.AssesedOutcomeSelectorForm()
        return context


# MetaProtocol
class MetaProtocolCreate(BaseCreate):
    success_message = 'Meta-protocol created.'
    parent_model = Study
    parent_template_name = 'study'
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDetail(BaseDetail):
    model = models.MetaProtocol


class MetaProtocolJSON(MetaProtocolDetail):
    http_method_names = ('get', )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(json_encode=True), content_type="application/json")


class MetaProtocolUpdate(BaseUpdate):
    success_message = "Meta-protocol updated."
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDelete(BaseDelete):
    success_message = "Meta-protocol deleted."
    model = models.MetaProtocol

    def get_success_url(self):
        self.parent = self.object.study
        return reverse("study:detail", kwargs={"pk": self.parent.pk})


# MetaResult
class MetaResultCreate(BaseCreateWithFormset):
    success_message = 'Meta-Result created.'
    parent_model = models.MetaProtocol
    parent_template_name = 'protocol'
    model = models.MetaResult
    form_class = forms.MetaResultForm
    formset_factory = forms.SingleResultFormset

    def get_form_kwargs(self):
        kwargs = super(MetaResultCreate, self).get_form_kwargs()

        # check if we have a template to use
        try:
            pk = int(self.request.GET.get('initial'))
        except Exception:
            pk = None

        if pk:
            obj = self.model.objects.filter(pk=pk).first()
            if obj and obj.get_assessment() == self.assessment:
                kwargs['instance'] = obj

        return kwargs

    def post_object_save(self, form, formset):
        # Bind newly created single-result outcome to meta-result instance
        for form in formset.forms:
            form.instance.meta_result = self.object

    def build_initial_formset_factory(self):

        def get_initial_data(field, **kwargs):
            formfield = field.formfield(**kwargs)
            if field.name == "study":
                formfield.queryset = formfield.queryset.filter(assessment=self.assessment, study_type=1)
            return formfield

        return modelformset_factory(models.SingleResult,
                                    form=forms.SingleResultForm,
                                    formset=forms.EmptySingleResultFormset,
                                    formfield_callback=get_initial_data,
                                    extra=1)


class MetaResultCopyAsNewSelector(MetaProtocolDetail):
    # Select an existing meta-result as a template for a new one
    template_name = 'epi/metaresult_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(MetaResultCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.MetaResultSelectorForm()
        return context


class MetaResultDetail(BaseDetail):
    model = models.MetaResult


class MetaResultJSON(MetaResultDetail):
    http_method_names = ('get', )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(json_encode=True), content_type="application/json")


class MetaResultUpdate(BaseUpdateWithFormset):
    success_message = "Meta-Result updated."
    model = models.MetaResult
    form_class = forms.MetaResultForm
    formset_factory = forms.SingleResultFormset

    def build_initial_formset_factory(self):
        formset = forms.SingleResultFormset(queryset=self.object.single_results.all().order_by('pk'))
        forms.meta_result_clean_update_formset(formset, self.assessment)
        return formset

    def post_object_save(self, form, formset):
        # Bind newly single-result outcome to meta-result instance, if adding new
        for form in formset.forms:
            form.instance.meta_result = self.object


class MetaResultDelete(BaseDelete):
    success_message = "Meta-Result deleted."
    model = models.MetaResult

    def get_success_url(self):
        self.parent = self.object.protocol
        return reverse("epi:mp_detail", kwargs={"pk": self.parent.pk})


class MetaResultFlat(BaseList):
    parent_model = Assessment
    model = models.MetaResult
    crud = "Read"

    def get_queryset(self):
        filters = {"protocol__study__assessment": self.assessment}
        perms = super(MetaResultFlat, self).get_obj_perms()
        if not perms['edit']:
            filters["protocol__study__published"] = True
        return self.model.objects.filter(**filters)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        export_format = request.GET.get("output", "excel")
        exporter = exports.MetaResultFlatDataPivot(
                self.object_list,
                export_format=export_format,
                filename='{}-epi-meta-analysis'.format(self.assessment))
        return exporter.build_response()


class MetaResultReport(GenerateReport):
    parent_model = Assessment
    model = models.MetaResult
    report_type = 4

    def get_queryset(self):
        filters = {"protocol__study__assessment": self.assessment}
        perms = super(MetaResultReport, self).get_obj_perms()
        if not perms['edit']:
            filters["protocol__study__published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "meta-results.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(queryset)


class MetaResultFullExport(MetaResultFlat):
    """
    Full XLS data export for the epidemiology meta-analyses.
    """

    def get(self, request, *args, **kwargs):
        self.object_list = super(MetaResultFullExport, self).get_queryset()
        exporter = exports.MetaResultFlatComplete(
                self.object_list,
                export_format="excel",
                filename='{}-epi-meta-analysis'.format(self.assessment),
                sheet_name='epi-meta-analysis')
        return exporter.build_response()
