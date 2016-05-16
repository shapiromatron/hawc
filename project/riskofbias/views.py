from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView

from assessment.models import Assessment
from riskofbias import exports, reports
from study.models import Study
from study.views import StudyList
from utils.views import (BaseCreate, BaseCreateWithFormset, BaseDetail,
                         BaseDelete, BaseList, BaseUpdate, BaseUpdateWithFormset,
                         GenerateFixedReport, MessageMixin,
                         ProjectManagerOrHigherMixin)

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


class ARoBCopy(ProjectManagerOrHigherMixin, MessageMixin, FormView):
    model = models.RiskOfBiasDomain
    template_name = "riskofbias/arob_copy.html"
    form_class = forms.RiskOfBiasCopyForm
    success_message = 'Risk of bias settings have been updated.'

    def get_assessment(self, request, *args, **kwargs):
        return self.assessment

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        return super(ARoBCopy, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ARoBCopy, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['assessment'] = self.assessment
        return kwargs

    def form_valid(self, form):
        form.copy_riskofbias()
        return super(ARoBCopy, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_detail',
                            kwargs={'pk': self.assessment.pk})


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
        return reverse_lazy('riskofbias:arob_reviewers',
                            kwargs={'pk': self.assessment.pk})


class ARoBReviewersUpdate(BaseUpdateWithFormset):
    """
    Creates the specified number of RiskOfBiases, one for each reviewer in the
    form. If the `number of reviewers` field is 1, then the only review is also
    the final review. If the `number of reviewers` field is more than one, then
    a final review is created in addition to the `number of reviewers`
    """
    model = Assessment
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    queryset = Assessment.objects.all()
    success_message = 'Risk of Bias reviewers updated.'
    template_name = "riskofbias/arob_reviewers_form.html"

    def build_initial_formset_factory(self):
        return self.formset_factory(
            queryset=Study.objects.filter(assessment=self.assessment))

    def pre_validate(self, form, formset):
        # if number_of_reviewers changes, change required on fields
        if 'number_of_reviewers' in form.changed_data:
            n = int(form.data['number_of_reviewers'])
            required_fields = ['reference_ptr', 'final_author']
            if n is 1:
                n = 0
            [required_fields.append('author-{}'.format(i)) for i in range(n)]
            for rob_form in formset.forms:
                for field in rob_form.fields:
                    if field not in required_fields:
                        rob_form.fields[field].required = False

    def post_object_save(self, form, formset):
        if 'number_of_reviewers' in form.changed_data:
            n = form.cleaned_data['number_of_reviewers']
            old_n = form.fields['number_of_reviewers'].initial
            n_diff = n - old_n
            # deactivate robs if number_of_reviewers is lowered.
            if n_diff < 0:
                if n is 1:
                    n = 0
                for rob_form in formset.forms:
                    deactivate_robs = rob_form.instance\
                                      .get_active_riskofbiases(with_final=False)[n:]
                    for rob in deactivate_robs:
                        rob.deactivate()
            # if n_of_r is increased, activate inactive robs with most recent last_updated
            else:
                for rob_form in formset.forms:
                    activate_robs = rob_form.instance.riskofbiases\
                                        .filter(active=False, final=False)\
                                        .order_by('last_updated')[:n]
                    for rob in activate_robs:
                        rob.activate()



    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_reviewers',
                            kwargs={'pk': self.assessment.pk})


# Risk-of-bias domain views
class RoBDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk-of-bias domain created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainUpdate(BaseUpdate):
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk-of-bias domain updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainDelete(BaseDelete):
    success_message = 'Risk-of-bias domain deleted.'
    model = models.RiskOfBiasDomain

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Risk-of-bias metric views
class RoBMetricCreate(BaseCreate):
    parent_model = models.RiskOfBiasDomain
    parent_template_name = 'domain'
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk-of-bias metric created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricUpdate(BaseUpdate):
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk-of-bias metric updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricDelete(BaseDelete):
    success_message = 'Risk-of-bias metric deleted.'
    model = models.RiskOfBiasMetric

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


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
        return reverse_lazy('riskofbias:rob_detail',
                            kwargs=self.kwargs)

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
        return reverse_lazy('riskofbias:robs_detail',
                            kwargs={'pk': self.object.study.pk})


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
        if context['obj_perms']['edit']:
            context['reviews'] = self.object.get_user_rob(self.request.user)
            context['finals'] = self.object.get_user_rob(self.request.user, final=True)
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
