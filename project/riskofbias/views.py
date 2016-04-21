from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.apps import apps
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from assessment.models import Assessment
from riskofbias import exports, reports
from study.models import Study
from study.views import StudyList
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, BaseDetail, BaseDelete,
                         BaseUpdate, BaseCreate, BaseList,
                         GenerateFixedReport, TeamMemberOrHigherMixin)

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


class ARoBReviewers(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    model = Assessment
    child_model = Study
    form_class = forms.NumberOfReviewersForm
    formset_factory = forms.RoBReviewerFormset
    crud = 'Update'
    template_name = "riskofbias/arob_reviewers.html"

    def get_success_url(self):
        return reverse_lazy('riskofbias:arob_detail', kwargs={'pk': self.assessment.pk})

    def post(self, request, *args, **kwargs):
        self.formset = self.formset_factory(request.POST)
        self.form = self.get_form(self.form_class)
        if self.form.is_valid() and self.formset.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid(self.form, self.formset)

    def form_valid(self):
        self.form.save()
        self.formset.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())
    #
    def get_context_data(self, **kwargs):
        context = super(ARoBReviewers, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            self.formset = self.formset_factory(
                queryset=Study.objects.filter(assessment=self.assessment))

        context['helper'] = forms.RoBReviewerFormsetHelper()
        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        return context
    #
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


class RoBsCreate(CanCreateMixin, MessageMixin, CreateView):
    model = Study
    template_name = "riskofbias/rob_edit.html"
    form_class = forms.RoBScoreForm
    success_message = 'Risk-of-bias information created.'
    crud = 'Create'

    def get_success_url(self):
        return reverse_lazy('riskofbias:robs_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        # only create if there are currently no study qualities with study
        if self.study.qualities.count()>0:
            raise Http404
        return super(RoBsCreate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.user_can_create_object(self.assessment):
            raise PermissionDenied

        self.formset = forms.RoBFormSet(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()

    def form_valid(self):
        for form in self.formset:
            sq = form.save(commit=False)
            sq.study = self.study
            sq.author = self.request.user
            sq.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            # build formset with initial data
            metrics = models.RiskOfBiasMetric \
                                     .get_required_metrics(self.assessment, self.study)
            robs = [{"study": self.study, "metric": metric}  for metric in metrics]
            NewRoBFormSet = modelformset_factory(models.RiskOfBias,
                                                form=forms.RoBScoreForm,
                                                formset=forms.BaseRoBFormSet,
                                                extra=len(robs))
            self.formset = NewRoBFormSet(queryset=models.RiskOfBias.objects.none(),
                                        initial=robs)

        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['study'] = self.study
        context['metric'] = [metric.description for metric in metrics]
        return context


class RoBsDetail(BaseDetail):
    """
    Detailed view of risk-of-bias metrics for reporting.
    """
    model = Study
    template_name = "riskofbias/rob_detail.html"

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(RoBsDetail, self).dispatch(*args, **kwargs)


class RoBsList(BaseList):
    model = Study
    template_name = 'riskofbias/rob_list.html'


class RoBsEdit(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Edit settings for risk-of-bias metrics associated with study.
    """
    model = Study
    template_name = "riskofbias/rob_edit.html"
    success_message = 'Risk-of-bias updated.'
    form_class = forms.RoBScoreForm
    formset_factory = forms.RoBFormSet
    crud = 'Update'

    def get_success_url(self):
        return reverse_lazy('riskofbias:robs_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(RoBsEdit, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formset = self.formset_factory(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid(author_form)
        else:
            return self.form_invalid(self.formset)

    def form_valid(self, author_form):
        self.formset.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(RoBsEdit, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            self.formset = self.formset_factory(
                queryset=models.RiskOfBias.objects.filter(study=self.study))

        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['study'] = self.study
        context['metric'] = [quality.metric.description for quality in self.study.qualities.all()]
        return context


class RoBsDelete(MessageMixin, AssessmentPermissionsMixin, DeleteView):
    """
    Delete all risk-of-bias metrics associated with study.
    """
    model = Study
    template_name = "riskofbias/rob_delete.html"
    form_class = forms.RoBScoreForm
    success_message = 'Risk-of-bias information deleted.'
    crud = 'Delete'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        models.RiskOfBias.objects.filter(study=self.object.pk).delete()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(reverse_lazy('study:detail',
                                    kwargs={'pk': self.object.pk}))

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(RoBsDelete, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['obj_perms'] = self.get_obj_perms()
        context['crud'] = self.crud
        return context


# Risk-of-bias views for endpoints
class RoBCreate(BaseCreate):
    success_message = 'Risk-of-bias override created.'
    model = models.RiskOfBias
    form_class = forms.RoBEndpointForm

    @property
    def parent_model(self):
        if self.kwargs['slug'] == "endpoint":
            return apps.get_model("animal", "Endpoint")
        else:
            raise Http404()

    @property
    def parent_template_name(self):
        if self.kwargs['slug'] == "endpoint":
            return "endpoint"
        else:
            raise Http404()


class RoBEdit(BaseUpdate):
    model = models.RiskOfBias
    form_class = forms.RoBEndpointForm
    success_message = 'Risk-of-bias metric updated.'

class RoBDelete(BaseDelete):
    model = models.RiskOfBias
    success_message = 'Risk-of-bias metric deleted.'

    def get_success_url(self):
        return self.object.study.get_absolute_url()
