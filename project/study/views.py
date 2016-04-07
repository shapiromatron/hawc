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

from assessment.models import Assessment
from lit.models import Reference
from riskofbias import exports, reports
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, BaseDetail, BaseDelete,
                         BaseVersion, BaseUpdate, BaseCreate,
                         BaseList, GenerateReport, GenerateFixedReport,
                         TeamMemberOrHigherMixin)

from . import models, forms


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
