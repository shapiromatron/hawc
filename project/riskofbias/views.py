from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from assessment.models import Assessment
from riskofbias import exports, reports
from study.models import Study
from study.views import StudyList
from utils.views import (BaseDetail, BaseDelete, BaseUpdate, BaseCreate,
                         BaseList, BaseUpdateWithFormset, BaseCreateWithFormset,
                         GenerateFixedReport)

from . import models, forms


# Assessment risk-of-bias requirements
class ARobList(StudyList):
    template_name = "riskofbias/study_list.html"


class ARoBDetail(BaseList):
    parent_model = Assessment
    model = models.RiskOfBiasDomain
    template_name = "riskofbias/arob_detail.html"

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)\
                                 .prefetch_related('metrics')


class ARoBEdit(ARoBDetail):
    crud = 'Update'


class ARoBReviewersList(BaseList):
    parent_model = Assessment
    model = Study
    template_name = 'riskofbias/arob_reviewers_list.html'

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)\
            .prefetch_related('riskofbiases')

    def get_context_data(self, **kwargs):
        context = super(ARoBReviewersList, self).get_context_data(**kwargs)
        robs_exist = sum([study.get_active_riskofbiases().count() for study in self.object_list])
        if robs_exist:
            context['form_crud'] = 'Update'
        else:
            context['form_crud'] = 'Create'
        context['rob_count'] = study.assessment.rob_settings.number_of_reviewers + 1
        return context

class ARoBReviewersCreate(BaseCreateWithFormset):
    model = Assessment
    child_model = models.RiskOfBias
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    success_message = 'Risk of Bias reviewers created.'
    template_name = "riskofbias/arob_reviewers_form.html"

    def build_initial_formset_factory(self):
        return self.formset_factory(
            queryset=Study.objects.filter(assessment=self.assessment))

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_reviewers', kwargs={'pk': self.assessment.pk})


class ARoBReviewersUpdate(BaseUpdateWithFormset):
    model = Assessment
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    queryset = Assessment.objects.all()
    success_message = 'Risk of Bias reviewers updated.'
    template_name = "riskofbias/arob_reviewers_form.html"


    def build_initial_formset_factory(self):
        return self.formset_factory(
            queryset=Study.objects.filter(assessment=self.assessment))

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_reviewers', kwargs={'pk': self.assessment.pk})


# Risk-of-bias domain views
class RoBDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk-of-bias domain created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


class RoBDomainUpdate(BaseUpdate):
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk-of-bias domain updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


class RoBDomainDelete(BaseDelete):
    success_message = 'Risk-of-bias domain deleted.'
    model = models.RiskOfBiasDomain

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


# Risk-of-bias metric views
class RoBMetricCreate(BaseCreate):
    parent_model = models.RiskOfBiasDomain
    parent_template_name = 'domain'
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk-of-bias metric created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


class RoBMetricUpdate(BaseUpdate):
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk-of-bias metric updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


class RoBMetricDelete(BaseDelete):
    success_message = 'Risk-of-bias metric deleted.'
    model = models.RiskOfBiasMetric

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update', kwargs={'pk': self.assessment.pk})


# Risk-of-bias views for study
class RoBFixedReport(GenerateFixedReport):
    parent_model = Assessment
    model = Study
    ReportClass = reports.RoBDOCXReport

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(RoBFixedReport, self).get_obj_perms()
        if not perms['edit']:
            filters["published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "riskofbias.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class StudyRoBExport(StudyList):
    """
    Full XLS data export for the risk-of-bias.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = super(StudyBiasExport, self).get_queryset()
        exporter = exports.RiskOfBiasFlatComplete(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias'.format(self.assessment),
            sheet_name='risk-of-bias'
        )
        return exporter.build_response()


class RoBEdit(BaseUpdate):
    """
    Edit settings for risk-of-bias metrics associated with study.
    """
    model = models.RiskOfBias
    template_name = "riskofbias/rob_edit.html"
    success_message = 'Risk-of-bias updated.'
    form_class = forms.RoBScoreForm
    formset_factory = forms.RoBFormSet

    def get_success_url(self):
        return reverse_lazy('riskofbias:rob_detail', kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        self.formset = self.formset_factory(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid(self.formset)

    def form_valid(self):
        self.formset.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(RoBEdit, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            self.formset = self.formset_factory(
            queryset=models.RiskOfBiasScore.objects.filter(riskofbias=self.object))

        context['formset'] = self.formset
        context['metric'] = [quality.metric.description for quality in self.object.scores.all()]
        return context


class RoBDelete(BaseDelete):
    """
    Delete all risk-of-bias metrics associated with study.
    """
    model = models.RiskOfBias
    template_name = "riskofbias/rob_delete.html"
    form_class = forms.RoBScoreForm
    success_message = 'Risk-of-bias information deleted.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:robs_detail', kwargs={'pk': self.object.study.pk})


class RoBDetail(BaseDetail):
    """
    Detailed view of risk-of-bias metrics for reporting.
    Displays RoB based on pk passed in url.

    For use in users updating owned reviews
    """
    model = models.RiskOfBias
    template_name = "riskofbias/rob_detail.html"


class RoBsDetail(BaseDetail):
    """
    Detailed view of risk-of-bias metrics for reporting.
    Displays RoB used as Study.qualities
    """
    model = Study
    template_name = 'riskofbias/robs_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RoBsDetail, self).get_context_data(**kwargs)
        context['reviews'] = self.object.get_user_rob(self.request.user)
        context['conflicts'] = self.object.get_user_rob(self.request.user, conflict=True)
        return context


class RoBsDetailAll(BaseDetail):
    """
    Detailed view of risk-of-bias metrics for reporting.
    Displays all active RoB in Study.

    TODO: Needs to have an updated JS RiskOfBias TblCompressed.
    """
    model = Study
    template_name = 'riskofbias/rob_detail_all.html'


class RoBsList(BaseList):
    model = Study
    template_name = 'riskofbias/rob_list.html'
