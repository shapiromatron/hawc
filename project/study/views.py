import json

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models.loading import get_model
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lit.models import Reference
from assessment.models import Assessment
from utils.helper import HAWCDjangoJSONEncoder
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, BaseDetail, BaseDelete,
                         BaseVersion, BaseUpdate, BaseCreate,
                         BaseList, GenerateReport)

from . import models, forms, exports


class StudyList(BaseList):
    parent_model = Assessment
    model = models.Study

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)

    def get_context_data(self, **kwargs):
        context = super(StudyList, self).get_context_data(**kwargs)
        if not context['obj_perms']['edit']:
            context['object_list'] = context['object_list'].filter(published=True)
        return context


class StudyReport(GenerateReport):
    parent_model = Assessment
    model = models.Study
    report_type = 1

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(StudyReport, self).get_obj_perms()
        if not perms['edit']:
            filters["published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "study.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(queryset)


class StudyBiasExport(StudyList):
    """
    Full XLS data export for the study bias.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = super(StudyBiasExport, self).get_queryset()
        exporter = exports.StudyQualityFlatComplete(
                self.object_list,
                export_format="excel",
                filename='{}-study-bias'.format(self.assessment),
                sheet_name='study-bias')
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
        search=get_model('lit', 'Search').objects.get(assessment=self.assessment,
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


class StudySearch(AssessmentPermissionsMixin, FormView):
    """ Returns JSON representations from study search. POST only."""
    template_name = "study/study_search.html"
    form_class = forms.StudySearchForm

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        self.permission_check_user_can_view()
        return super(StudySearch, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs['assessment_pk'] = self.assessment.pk
        return kwargs

    def get(self, request, *args, **kwargs):
        raise Http404

    def form_invalid(self, form):
        return HttpResponse(json.dumps({"status": "fail",
                                        "studies": [],
                                        "error": "invalid form format"}),
                            content_type="application/json")

    def form_valid(self, form):
        studies = form.search()
        return HttpResponse(json.dumps({"status": "success",
                                        "studies": studies},
                                       cls=HAWCDjangoJSONEncoder),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(StudySearch, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class StudyReadJSON(BaseDetail):
    model = models.Study

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(), content_type="application/json")


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


# Assessment study-quality requirements
class ASQDetail(BaseList):
    parent_model = Assessment
    model = models.StudyQualityDomain
    template_name = "study/asq_detail.html"

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)\
                                 .prefetch_related('metrics')


class ASQEdit(ASQDetail):
    crud = 'Update'


# Study quality domain views
class SQDomainCreate(BaseCreate):
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.StudyQualityDomain
    form_class = forms.SQDomainForm
    success_message = 'Study quality domain created.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQDomainUpdate(BaseUpdate):
    model = models.StudyQualityDomain
    form_class = forms.SQDomainForm
    success_message = 'Study quality domain updated.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQDomainDelete(BaseDelete):
    success_message = 'Study quality domain deleted.'
    model = models.StudyQualityDomain

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


# Study quality metric views
class SQMetricCreate(BaseCreate):
    parent_model = models.StudyQualityDomain
    parent_template_name = 'domain'
    model = models.StudyQualityMetric
    form_class = forms.SQMetricForm
    success_message = 'Study quality metric created.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQMetricUpdate(BaseUpdate):
    model = models.StudyQualityMetric
    form_class = forms.SQMetricForm
    success_message = 'Study quality metric updated.'

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


class SQMetricDelete(BaseDelete):
    success_message = 'Study quality metric deleted.'
    model = models.StudyQualityMetric

    def get_success_url(self):
        return reverse_lazy('study:asq_update', kwargs={'pk': self.assessment.pk})


# Study quality views
class SQCreate(CanCreateMixin, MessageMixin, CreateView):
    model = models.Study
    template_name = "study/sq_edit.html"
    form_class = forms.SQForm
    success_message = 'Study-quality information created.'
    crud = 'Create'

    def get_success_url(self):
        return reverse_lazy('study:sq_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        # only create if there are currently no study qualities with study
        if self.study.qualities.count()>0:
            raise Http404
        return super(SQCreate, self).dispatch(*args, **kwargs)

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
            sq.study = self.study
            sq.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            # build formset with initial data
            metrics = models.StudyQualityMetric \
                                     .get_required_metrics(self.assessment, self.study)
            sqs = [{"study": self.study, "metric": metric}  for metric in metrics]
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
        return context


class SQDetail(AssessmentPermissionsMixin, DetailView):
    """
    Detailed view of study-quality metrics for reporting.
    """
    model = models.Study
    template_name = "study/sq_detail.html"
    crud = 'Read'

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['sqs'] = self.object.qualities.all().select_related('metric')
        context['obj_perms'] = super(SQDetail, self).get_obj_perms()
        context['crud'] = self.crud
        return context


class SQEdit(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Edit settings for study quality metrics associated with study.
    """
    model = models.Study
    template_name = "study/sq_edit.html"
    form_class = forms.SQForm
    success_message = 'Study quality updated.'
    crud = 'Update'

    def get_success_url(self):
        return reverse_lazy('study:sq_detail', kwargs={'pk': self.study.pk})

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQEdit, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formset = forms.SQFormSet(self.request.POST)
        if self.formset.is_valid():
            return self.form_valid()
        else:
            self.object = self.study
            return self.form_invalid(formset=self.formset)

    def form_valid(self):
        self.formset.save()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            self.formset = forms.SQFormSet(queryset=models.StudyQuality.objects.filter(study=self.study))

        context['formset'] = self.formset
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['study'] = self.study
        return context


class SQDelete(MessageMixin, AssessmentPermissionsMixin, DeleteView):
    """
    Delete all study quality-metrics associated with study.
    """
    model = models.Study
    template_name = "study/sq_delete.html"
    form_class = forms.SQForm
    success_message = 'Study-quality information deleted.'
    crud = 'Delete'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        models.StudyQuality.objects.filter(study=self.object.pk).delete()
        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(reverse_lazy('study:detail',
                                    kwargs={'pk': self.object.pk}))

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(self.model, pk=kwargs['pk'])
        self.assessment = self.study.get_assessment()
        return super(SQDelete, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['sqs'] = self.object.qualities.all().select_related('metric')
        context['obj_perms'] = super(SQDelete, self).get_obj_perms()
        context['crud'] = self.crud
        return context


class SQAggHeatmap(BaseList):
    parent_model = Assessment
    model = models.Study
    template_name = "study/sq_agg.html"

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)

    def get_context_data(self, **kwargs):
        context = super(SQAggHeatmap, self).get_context_data(**kwargs)
        jsons = [study.get_json(json_encode=False) for study in self.object_list]
        context['object_list_json'] = json.dumps(jsons, cls=HAWCDjangoJSONEncoder)
        context['chart_type'] = 'heatmap'
        return context


class SQAggStacked(SQAggHeatmap):

    def get_context_data(self, **kwargs):
        context = super(SQAggStacked, self).get_context_data(**kwargs)
        context['chart_type'] = 'stacked'
        return context
