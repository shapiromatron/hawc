from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import BaseList
from ..study.models import Study
from . import forms, models


class StudyLevelValues(BaseList):
    parent_model = Study
    model = models.StudyLevelValue
    template_name = "animalv2/studylevelvalues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(study=self.parent)
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(study=self.parent).order_by("-created")
        return queryset


class StudyLevelValueViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Study
    model = models.StudyLevelValue

    form_fragment = "animalv2/fragments/studylevelvalue_edit_row.html"
    detail_fragment = "animalv2/fragments/studylevelvalue_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        # tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
        # prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
        # models.Workflow.annotate_tag_parents([request.item.object], tags)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = forms.StudyLevelValueForm(data=form_data, parent=request.item.parent)
        context = self.get_context_data(form=form)
        if request.method == "POST" and form.is_valid():
            self.perform_create(request.item, form)
            template = self.detail_fragment
            context.update(object=request.item.object)
            # tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
            # prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
            # models.Workflow.annotate_tag_parents([request.item.object], tags)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = forms.StudyLevelValueForm(data=form_data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
            # tags = models.ReferenceFilterTag.get_assessment_qs(request.item.assessment.id)
            # prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
            # models.Workflow.annotate_tag_parents([request.item.object], tags)
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        form = forms.StudyLevelValueForm(data=None, instance=request.item.object)
        context = self.get_context_data(form=form)
        return render(request, self.form_fragment, context)
