from django.core.urlresolvers import reverse_lazy
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView

from assessment.models import Assessment
from riskofbias import exports, reports
from study.models import Study
from study.views import StudyList
from utils.views import (BaseCreate, BaseDetail, BaseDelete, BaseList,
                         BaseUpdate, BaseUpdateWithFormset,
                         GenerateFixedReport, MessageMixin,
                         TeamMemberOrHigherMixin, IsAuthorMixin,
                         ProjectManagerOrHigherMixin)

from . import models, forms


# Assessment risk of bias requirements
class ARoBDetail(BaseList):
    parent_model = Assessment
    model = models.RiskOfBiasDomain
    template_name = 'riskofbias/arob_detail.html'

    def get_queryset(self):
        return self.model.objects\
            .filter(assessment=self.assessment)\
            .prefetch_related('metrics')


class ARoBEdit(ProjectManagerOrHigherMixin, ARoBDetail):
    crud = 'Update'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])


class ARoBCopy(ProjectManagerOrHigherMixin, MessageMixin, FormView):
    model = models.RiskOfBiasDomain
    template_name = 'riskofbias/arob_copy.html'
    form_class = forms.RiskOfBiasCopyForm
    success_message = 'Risk of bias settings have been updated.'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs['pk'])

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


class ARoBReviewersList(TeamMemberOrHigherMixin, BaseList):
    """
    List an assessment's studies with their active risk of bias reviewers.
    """
    parent_model = Assessment
    model = Study
    template_name = 'riskofbias/reviewers_list.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])

    def get_queryset(self):
        return self.model.objects\
            .filter(assessment=self.assessment)\
            .prefetch_related(
                Prefetch(
                    'riskofbiases',
                    queryset=models.RiskOfBias.objects
                                   .filter(active=True)
                                   .prefetch_related('author'),
                    to_attr='active_riskofbiases'))

    def get_context_data(self, **kwargs):
        context = super(ARoBReviewersList, self).get_context_data(**kwargs)
        context['rob_count'] = self.assessment.rob_settings.number_of_reviewers + 1
        return context


class ARoBReviewersUpdate(ProjectManagerOrHigherMixin, BaseUpdateWithFormset):
    """
    Creates the specified number of RiskOfBiases, one for each reviewer in the
    form. If the `number of reviewers` field is 1, then the only review is also
    the final review. If the `number of reviewers` field is more than one, then
    a final review is created in addition to the `number of reviewers`
    """
    model = Assessment
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    success_message = 'Risk of Bias reviewers updated.'
    template_name = 'riskofbias/reviewers_form.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs['pk'])

    def build_initial_formset_factory(self):
        queryset = Study.objects.filter(assessment=self.assessment)\
            .prefetch_related('identifiers')\
            .prefetch_related('searches')\
            .prefetch_related('assessment__rob_settings')\
            .prefetch_related(
                Prefetch(
                    'riskofbiases',
                    queryset=models.RiskOfBias.objects
                                   .filter(active=True, final=False),
                    to_attr='active_riskofbiases')
                )

        return self.formset_factory(queryset=queryset)

    def pre_validate(self, form, formset):
        # if number_of_reviewers changes, change required on fields
        if 'number_of_reviewers' in form.changed_data:
            n = int(form.data['number_of_reviewers'])
            required_fields = ['reference_ptr', 'final_author']
            if n == 1:
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
                if n == 1:
                    n = 0
                for rob_form in formset.forms:
                    deactivate_robs = rob_form.instance\
                                      .get_active_robs(with_final=False)[n:]
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


# Risk of bias domain views
class RoBDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk of bias domain created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainUpdate(BaseUpdate):
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Risk of bias domain updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainDelete(BaseDelete):
    success_message = 'Risk of bias domain deleted.'
    model = models.RiskOfBiasDomain

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Risk of bias metric views
class RoBMetricCreate(BaseCreate):
    parent_model = models.RiskOfBiasDomain
    parent_template_name = 'domain'
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk of bias metric created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricUpdate(BaseUpdate):
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Risk of bias metric updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricDelete(BaseDelete):
    success_message = 'Risk of bias metric deleted.'
    model = models.RiskOfBiasMetric

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Risk of bias views for study
class RoBFixedReport(GenerateFixedReport):
    parent_model = Assessment
    model = Study
    ReportClass = reports.RoBDOCXReport

    def get_queryset(self):
        filters = {'assessment': self.assessment}
        perms = super(RoBFixedReport, self).get_obj_perms()
        if not perms['edit']:
            filters['published'] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return 'riskofbias.docx'

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class StudyRoBPublicExport(StudyList):
    """
    Full XLS data export for the risk of bias.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = super(StudyRoBPublicExport, self).get_queryset()
        exporter = exports.RiskOfBiasFlatPublic(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias-public'.format(self.assessment),
            sheet_name='risk of bias'
        )
        return exporter.build_response()


class StudyRoBCompleteExport(TeamMemberOrHigherMixin, StudyList):
    """
    Full XLS data export for the risk-of-bias.
    """
    def get_assessment(self, request, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs['pk'])
        return self.parent.get_assessment()

    def get(self, request, *args, **kwargs):
        self.object_list = super(StudyRoBCompleteExport, self).get_queryset()
        exporter = exports.RiskOfBiasFlatComplete(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias-complete'.format(self.assessment),
            sheet_name='risk of bias'
        )
        return exporter.build_response()


# RoB views
class RoBDetail(BaseDetail):
    """
    Detailed view of risk of bias metrics for reporting.
    Displays RoB used as Study.qualities
    """
    model = Study
    template_name = 'riskofbias/rob_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RoBDetail, self).get_context_data(**kwargs)
        if context['obj_perms']['edit']:
            context['reviews'] = self.object\
                .get_user_robs(self.request.user)
            context['final'] = self.object\
                .get_user_robs(self.request.user, final=True).first()
        return context


class RoBsDetailAll(TeamMemberOrHigherMixin, RoBDetail):
    """
    Detailed view of risk of bias metrics for reporting.
    Displays all active RoB in Study.
    """
    template_name = 'riskofbias/rob_detail_all.html'

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Study, pk=kwargs['pk'])
        return self.object.get_assessment()


class RoBEdit(IsAuthorMixin, BaseUpdate):
    """
    Edit settings for risk of bias metrics associated with study.
    """
    model = models.RiskOfBias
    template_name = 'riskofbias/rob_edit.html'
    success_message = 'Risk of bias updated.'
    form_class = forms.RoBScoreForm
    formset_factory = forms.RoBFormSet

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
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
                queryset=models.RiskOfBiasScore.objects
                               .filter(riskofbias=self.object))

        context['formset'] = self.formset
        context['metric'] = [
            quality.metric.description
            for quality in self.object.scores.all()
        ]
        return context


class RoBEditFinal(IsAuthorMixin, BaseDetail):
    """
    Displays a form for editing the risk of bias metrics for the final review.
    Also displays the metrics for the other active risk of bias reviews.
    """
    model = models.RiskOfBias
    template_name = 'riskofbias/rob_edit_final.html'
