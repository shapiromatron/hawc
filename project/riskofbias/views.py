from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView

from assessment.models import Assessment
from riskofbias import exports
from study.models import Study
from study.views import StudyList
from utils.views import (BaseCreate, BaseDetail, BaseDelete, BaseList,
                         BaseUpdate, BaseUpdateWithFormset,
                         MessageMixin, TeamMemberOrHigherMixin,
                         TimeSpentOnPageMixin,
                         ProjectManagerOrHigherMixin)

from . import models, forms


# Assessment Study Evaluation requirements
class ARoBDetail(BaseList):
    parent_model = Assessment
    model = models.RiskOfBiasDomain
    template_name = 'riskofbias/arob_detail.html'

    def get_queryset(self):
        return self.model.objects\
            .get_qs(self.assessment)\
            .prefetch_related('metrics')


class ARoBEdit(ProjectManagerOrHigherMixin, ARoBDetail):
    crud = 'Update'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])


class ARoBCopy(ProjectManagerOrHigherMixin, MessageMixin, FormView):
    model = models.RiskOfBiasDomain
    parent_model = Assessment
    template_name = 'riskofbias/arob_copy.html'
    form_class = forms.RiskOfBiasCopyForm
    success_message = 'Study Evaluation settings have been updated.'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['assessment'] = self.assessment
        return kwargs

    def form_valid(self, form):
        form.copy_riskofbias()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_detail',
                            kwargs={'pk': self.assessment.pk})


class ARoBReviewersList(TeamMemberOrHigherMixin, BaseList):
    """
    List an assessment's studies with their active Study Evaluation reviewers.
    """
    parent_model = Assessment
    model = Study
    template_name = 'riskofbias/reviewers_list.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=kwargs['pk'])

    def get_queryset(self):
        return self.model.objects\
            .get_qs(self.assessment)\
            .prefetch_related(
                Prefetch(
                    'riskofbiases',
                    queryset=models.RiskOfBias.objects.all_active()
                                   .prefetch_related('author'),
                    to_attr='active_riskofbiases'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    success_message = 'Study Evaluation reviewers updated.'
    template_name = 'riskofbias/reviewers_form.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.model, pk=kwargs['pk'])

    def build_initial_formset_factory(self):
        queryset = Study.objects.get_qs(self.assessment)\
            .prefetch_related('identifiers')\
            .prefetch_related('searches')\
            .prefetch_related('assessment__rob_settings')\
            .prefetch_related(
                Prefetch(
                    'riskofbiases',
                    queryset=models.RiskOfBias.objects.active(),
                    to_attr='active_riskofbiases')
                )

        return self.formset_factory(queryset=queryset)

    def pre_validate(self, form, formset):
        # if number_of_reviewers changes, change required on fields
        if form.is_valid() and 'number_of_reviewers' in form.changed_data:
            n = form.cleaned_data['number_of_reviewers']
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


# Study Evaluation domain views
class RoBDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Study Evaluation domain created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainUpdate(BaseUpdate):
    model = models.RiskOfBiasDomain
    form_class = forms.RoBDomainForm
    success_message = 'Study Evaluation domain updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBDomainDelete(BaseDelete):
    success_message = 'Study Evaluation domain deleted.'
    model = models.RiskOfBiasDomain

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Study Evaluation metric views
class RoBMetricCreate(BaseCreate):
    parent_model = models.RiskOfBiasDomain
    parent_template_name = 'domain'
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Study Evaluation metric created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricUpdate(BaseUpdate):
    model = models.RiskOfBiasMetric
    form_class = forms.RoBMetricForm
    success_message = 'Study Evaluation metric updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricDelete(BaseDelete):
    success_message = 'Study Evaluation metric deleted.'
    model = models.RiskOfBiasMetric

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Study Evaluation metric views for custom or default answers
class RoBMetricAnswersCreate(BaseCreate):
    parent_model = models.RiskOfBiasMetric
    parent_template_name = 'metric'
    model = models.RiskOfBiasMetricAnswers
    form_class = forms.RoBMetricAnswersForm
    success_message  = 'Study Evaluation metric answer created.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricAnswersUpdate(BaseUpdate):
    model = models.RiskOfBiasMetricAnswers
    form_class = forms.RoBMetricAnswersForm
    success_message = 'Study Evaluation metric answers updated.'

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


class RoBMetricAnswersDelete(BaseDelete):
    success_message = 'Study Evaluation metric answers deleted.'
    model = models.RiskOfBiasMetricAnswers

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_update',
                            kwargs={'pk': self.assessment.pk})


# Study Evaluation views for study
class StudyRoBExport(StudyList):
    """
    Full XLS data export for the Study Evaluation.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = super().get_queryset()
        exporter = exports.RiskOfBiasFlat(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias'.format(self.assessment),
            sheet_name='risk of bias'
        )
        return exporter.build_response()


class StudyRoBCompleteExport(TeamMemberOrHigherMixin, StudyList):
    """
    Full XLS data export for the risk-of-bias.
    """
    def get_assessment(self, request, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs['pk'])
        return self.parent

    def get(self, request, *args, **kwargs):
        self.object_list = super().get_queryset()
        exporter = exports.RiskOfBiasCompleteFlat(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias-complete'.format(self.assessment),
            sheet_name='risk of bias'
        )
        return exporter.build_response()


# RoB views
class RoBDetail(BaseDetail):
    """
    Detailed view of final Study Evaluation metric.
    """
    model = Study
    template_name = 'riskofbias/rob_detail.html'


class RoBsDetailAll(TeamMemberOrHigherMixin, RoBDetail):
    """
    Detailed view of all active Study Evaluation metric, including final.
    """
    template_name = 'riskofbias/rob_detail_all.html'

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Study, pk=kwargs['pk'])
        return self.object.get_assessment()


class RoBEdit(TimeSpentOnPageMixin, BaseDetail):
    """
    Displays a form for editing the Study Evaluation metrics for the final review.
    Also displays the metrics for the other active Study Evaluation reviews.
    """
    model = models.RiskOfBias
    template_name = 'riskofbias/rob_edit.html'

    def get_object(self, **kwargs):
        # either project managers OR the author can edit/view.
        obj = super().get_object(**kwargs)
        if obj.author != self.request.user and \
            not self.assessment.user_can_edit_assessment(self.request.user):
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.request.META['HTTP_REFERER'] \
            if 'HTTP_REFERER' in self.request.META \
            else self.object.get_absolute_url()
        context['hero_id'] = Study.objects.prefetch_related('identifiers').filter(identifiers__database=2).values_list('identifiers__unique_id', flat=True)
        return context
