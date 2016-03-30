import json
import itertools

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.apps import apps
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lit.models import Reference
from assessment.models import Assessment
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, BaseDetail, BaseDelete,
                         BaseVersion, BaseUpdate, BaseCreate,
                         BaseList, GenerateReport, GenerateFixedReport,
                         TeamMemberOrHigherMixin)

from . import models, forms, exports, reports


class StudyList(BaseList):
    parent_model = Assessment
    model = models.Study

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class StudyReport(GenerateReport):
    parent_model = Assessment
    model = models.Study
    report_type = 1

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(StudyReport, self).get_obj_perms()
        if not perms['edit'] or self.onlyPublished:
            filters["published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "study.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(queryset)


class StudyBiasExport(StudyList):
    """
    Full XLS data export for the risk-of-bias.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = super(StudyBiasExport, self).get_queryset()
        exporter = exports.StudyQualityFlatComplete(
            self.object_list,
            export_format="excel",
            filename='{}-risk-of-bias'.format(self.assessment),
            sheet_name='risk-of-bias'
        )
        return exporter.build_response()


class StudyCreateFromReference(BaseCreate):
    """
    Create view of Study, given a lit.Reference already exists. This is more
    difficult because we must pass the reference object to the newly created
    study.
    """
    parent_model = Reference
    parent_template_name = 'reference'
    model = models.Study
    form_class = forms.NewStudyFromReferenceForm
    success_message = 'Study created.'

    def get_initial(self):
        self.initial = {"reference": self.parent,
                        "short_citation": self.parent.get_short_citation_estimate(),
                        "full_citation": self.parent.reference_citation}
        return self.initial

    def get(self, request, *args, **kwargs):
        if self.model.objects.filter(pk=self.parent.pk).count()>0:
            raise Http404
        return super(StudyCreateFromReference, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.model.objects.filter(pk=self.parent.pk).count()>0:
            raise Http404

        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        #hack- this will fail but will also create errors if needed
        try:
           form.is_valid()
        except:
            pass

        # hack - use custom validation since will always fail for one-to-one
        if ((form.data['short_citation'] == u'') or
            (form.data['full_citation'] == u'') or
            (form.data['study_type'] == u'')):
            return self.form_invalid(form)
        else:
            #save using our custom saving tool
            dt = dict(form.data)
            dt.pop('_wysihtml5_mode')
            dt.pop('csrfmiddlewaretoken')
            dt.pop('save')  # crispyform
            for k,v in dt.iteritems(): #unpack list
                dt[k]=v[0]
            self.object = self.model.save_new_from_reference(self.parent, dt)

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())


class ReferenceStudyCreate(BaseCreate):
    """
    Creation of both a reference and study. Easier because there is no
    existing Reference instance in table, so we just create both at once.
    """
    success_message = 'Study created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Study
    form_class = forms.ReferenceStudyForm

    def form_valid(self, form):
        self.object = form.save()
        search=apps.get_model('lit', 'Search').objects.get(assessment=self.assessment,
                                                      source=0, #manual import
                                                      title="Manual import")
        self.object.searches.add(search)
        return super(ReferenceStudyCreate, self).form_valid(form)


class StudyRead(BaseDetail):
    model = models.Study

    def get_context_data(self, **kwargs):
        context = super(StudyRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "study"
        context['comment_object_id'] = self.object.pk
        context['attachments_viewable'] = self.assessment.user_can_view_attachments(self.request.user)
        return context


class StudyUpdate(BaseUpdate):
    model = models.Study
    form_class = forms.StudyForm
    success_message = 'Study updated.'


class StudyDelete(BaseDelete):
    model = models.Study
    success_message = 'Study deleted.'

    def get_success_url(self):
        return reverse_lazy('study:list', kwargs={'pk': self.assessment.pk})


class StudyVersions(BaseVersion):
    model = models.Study
    template_name = "study/study_versions.html"


class StudiesCopy(TeamMemberOrHigherMixin, MessageMixin, FormView):
    """
    Copy one or more studies from one assessment to another. This will copy
    all nested data as well.
    """
    template_name = "study/studies_copy.html"
    form_class = forms.StudiesCopy

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super(StudiesCopy, self).get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super(StudiesCopy, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['assessment'] = self.assessment
        return kwargs

    def form_valid(self, form):
        models.Study.copy_across_assessments(
            form.cleaned_data['studies'],
            form.cleaned_data['assessment'])
        msg = "Studies copied!"
        self.success_message = msg
        return super(StudiesCopy, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('study:list', kwargs={'pk': self.assessment.id})


# Attachment views
class AttachmentCreate(BaseCreate):
    success_message = 'Attachment added to study.'
    parent_model = models.Study
    parent_template_name = 'study'
    model = models.Attachment
    form_class = forms.AttachmentForm

    def get_success_url(self):
        return reverse_lazy('study:detail', kwargs={'pk': self.parent.pk})


class AttachmentDelete(BaseDelete):
    success_message = 'Attachment deleted.'
    model = models.Attachment

    def get_success_url(self):
        self.parent = self.object.study
        return reverse_lazy('study:detail', kwargs={'pk': self.parent.pk})


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_can_view_attachments(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            return PermissionDenied


# Assessment risk-of-bias requirements
class ASQDetail(BaseList):
    parent_model = Assessment
    model = models.StudyQualityDomain
    template_name = "study/asq_detail.html"

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)\
                                 .prefetch_related('metrics')


class ASQEdit(ASQDetail):
    crud = 'Update'


# Risk-of-bias domain views
class SQDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.StudyQualityDomain
    form_class = forms.SQDomainForm
    success_message = 'Risk-of-bias domain created.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQDomainUpdate(BaseUpdate):
    model = models.StudyQualityDomain
    form_class = forms.SQDomainForm
    success_message = 'Risk-of-bias domain updated.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQDomainDelete(BaseDelete):
    success_message = 'Risk-of-bias domain deleted.'
    model = models.StudyQualityDomain

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


# Risk-of-bias metric views
class SQMetricCreate(BaseCreate):
    parent_model = models.StudyQualityDomain
    parent_template_name = 'domain'
    model = models.StudyQualityMetric
    form_class = forms.SQMetricForm
    success_message = 'Risk-of-bias metric created.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQMetricUpdate(BaseUpdate):
    model = models.StudyQualityMetric
    form_class = forms.SQMetricForm
    success_message = 'Risk-of-bias metric updated.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQMetricDelete(BaseDelete):
    success_message = 'Risk-of-bias metric deleted.'
    model = models.StudyQualityMetric

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


# Risk-of-bias views for study
class SQFixedReport(GenerateFixedReport):
    parent_model = Assessment
    model = models.Study
    ReportClass = reports.SQDOCXReport

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(SQFixedReport, self).get_obj_perms()
        if not perms['edit']:
            filters["published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "risk_of_bias.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class SQsCreate(CanCreateMixin, MessageMixin, CreateView):
    model = models.Study
    template_name = "study/sq_edit.html"
    form_class = forms.SQForm
    success_message = 'Risk-of-bias information created.'
    crud = 'Create'

    def get_success_url(self):
        return reverse_lazy('study:sqs_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        # only create if there are currently no study qualities with study
        if self.study.qualities.count()>0:
            raise Http404
        return super(SQsCreate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.user_can_create_object(self.assessment):
            raise PermissionDenied

        self.formset = forms.SQFormSet(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()

    def form_valid(self):
        for form in self.formset:
            sq = form.save(commit=False)
            sq.content_object = self.study
            sq.author = self.request.user
            sq.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            # build formset with initial data
            metrics = models.StudyQualityMetric \
                                     .get_required_metrics(self.assessment, self.study)
            sqs = [{"content_object": self.study, "metric": metric}  for metric in metrics]
            NewSQFormSet = modelformset_factory(models.StudyQuality,
                                                form=forms.SQForm,
                                                formset=forms.BaseSQFormSet,
                                                extra=len(sqs))
            self.formset = NewSQFormSet(queryset=models.StudyQuality.objects.none(),
                                        initial=sqs)

        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['study'] = self.study
        context['metric'] = [metric.description for metric in metrics]
        return context


class SQsDetail(BaseDetail):
    """
    Detailed view of risk-of-bias metrics for reporting.
    """
    model = models.Study
    template_name = "study/sq_detail.html"

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQsDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SQsDetail, self).get_context_data(**kwargs)
        context['sqs'] = self.object.qualities.all().select_related('metric')
        return context


class SQsEdit(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Edit settings for risk-of-bias metrics associated with study.
    """
    model = models.Study
    template_name = "study/sq_edit.html"
    success_message = 'Risk-of-bias updated.'
    author_form = forms.SQAuthorForm
    form_class = forms.SQForm
    formset_factory = forms.SQFormSet
    crud = 'Update'

    def get_success_url(self):
        return reverse_lazy('study:sqs_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQsEdit, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        author_form = self.author_form(self.request.POST)
        self.formset = self.formset_factory(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid(author_form)
        else:
            return self.form_invalid(self.formset)

    def form_valid(self, author_form):
        """
            author_form is only shown if SQs have no author, so can only be
            changed if SQs have no author and authorship is taken.
        """
        if author_form.has_changed():
            for form in self.formset:
                sq = form.save(commit=False)
                sq.content_object = self.study
                sq.author = self.request.user
                sq.save()
        else:
            self.formset.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(SQsEdit, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            self.formset = self.formset_factory(queryset=models.StudyQuality.objects.filter(studies=self.study))

        if self.study.qualities.filter(author__isnull=True).exists():
            context['author_form'] = self.author_form
        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['study'] = self.study
        context['metric'] = [quality.metric.description for quality in self.study.qualities.all()]
        return context


class SQsDelete(MessageMixin, AssessmentPermissionsMixin, DeleteView):
    """
    Delete all risk-of-bias metrics associated with study.
    """
    model = models.Study
    template_name = "study/sq_delete.html"
    form_class = forms.SQForm
    success_message = 'Risk-of-bias information deleted.'
    crud = 'Delete'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        models.StudyQuality.objects.filter(studies=self.object.pk).delete()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(reverse_lazy('study:detail',
                                    kwargs={'pk': self.object.pk}))

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQsDelete, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['sqs'] = self.object.qualities.all().select_related('metric')
        context['obj_perms'] = self.get_obj_perms()
        context['crud'] = self.crud
        return context


# Risk-of-bias views for endpoints
class SQCreate(BaseCreate):
    success_message = 'Risk-of-bias override created.'
    model = models.StudyQuality
    form_class = forms.SQEndpointForm

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


class SQEdit(BaseUpdate):
    model = models.StudyQuality
    form_class = forms.SQEndpointForm
    success_message = 'Risk-of-bias metric updated.'

    def get_context_data(self, **kwargs):
        context = super(SQEdit, self).get_context_data(**kwargs)
        if type(self.object.content_object) == apps.get_model("animal", "Endpoint"):
            context["endpoint"] = self.object.content_object
        return context


class SQDelete(BaseDelete):
    model = models.StudyQuality
    success_message = 'Risk-of-bias metric deleted.'

    def get_context_data(self, **kwargs):
        context = super(SQDelete, self).get_context_data(**kwargs)
        if type(self.object.content_object) == apps.get_model("animal", "Endpoint"):
            context["endpoint"] = self.object.content_object
        return context

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()
