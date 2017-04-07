from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView

from assessment.models import Assessment
from lit.models import Reference
from mgmt.views import EnsurePreparationStartedMixin
from utils.views import (MessageMixin, BaseDetail, BaseDelete,
                         BaseUpdate, BaseCreate, BaseList,
                         GenerateReport, TeamMemberOrHigherMixin)

from . import models, forms


class StudyList(BaseList):
    parent_model = Assessment
    model = models.Study

    def get_queryset(self):
        return self.model.objects.get_qs(self.assessment.id)


class StudyReport(GenerateReport):
    parent_model = Assessment
    model = models.Study
    report_type = 1

    def get_queryset(self):
        perms = super(StudyReport, self).get_obj_perms()
        if not perms['edit'] or self.onlyPublished:
            return self.model.objects.published(self.assessment.id)
        return self.model.objects.get_qs(self.assessment.id)

    def get_filename(self):
        return "study.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(queryset)


class StudyCreateFromReference(EnsurePreparationStartedMixin, BaseCreate):
    # Create Study from an existing lit.Reference.

    parent_model = Reference
    parent_template_name = 'reference'
    model = models.Study
    form_class = forms.NewStudyFromReferenceForm
    success_message = 'Study created.'

    def dispatch(self, *args, **kwargs):
        # ensure if study already exists you can't create another
        study = self.model.objects.filter(pk=kwargs['pk']).first()
        if study:
            return HttpResponseRedirect(study.get_update_url())
        return super(StudyCreateFromReference, self).dispatch(*args, **kwargs)

    def get_initial(self):
        self.initial = dict(
            assessment=self.assessment,
            reference=self.parent,
            short_citation=self.parent.get_short_citation_estimate(),
            full_citation=self.parent.reference_citation
        )
        return self.initial

    def get_form(self, form_class=None):
        form = super(StudyCreateFromReference, self).get_form(form_class)
        form.instance.assessment = self.assessment
        return form

    def form_valid(self, form):
        self.object = self.model.save_new_from_reference(self.parent, form.cleaned_data)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())


class ReferenceStudyCreate(EnsurePreparationStartedMixin, BaseCreate):
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
        search = apps.get_model('lit', 'Search').objects.get_manually_added(self.assessment)
        self.object.searches.add(search)
        return super(ReferenceStudyCreate, self).form_valid(form)


class StudyRead(BaseDetail):
    model = models.Study

    def get_context_data(self, **kwargs):
        context = super(StudyRead, self).get_context_data(**kwargs)
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


class StudiesCopy(TeamMemberOrHigherMixin, MessageMixin, FormView):
    """
    Copy one or more studies from one assessment to another. This will copy
    all nested data as well.
    """
    model = Assessment
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


class StudyRoBRedirect(StudyRead):
    # permanent redirect of RoB results; link is required to work based on
    # older OHAT reports which use this legacy URL route.

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return redirect(self.object.get_final_rob_url(), permanent=True)


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
