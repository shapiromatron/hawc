from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import BaseCreate, BaseDelete, BaseDetail, BaseUpdate
from ..study.models import Study
from . import forms, models


# Design
class DesignCreate(BaseCreate):
    success_message = "Study design created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm

    def get_success_url(self):
        return self.object.get_update_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DesignUpdate(BaseUpdate):
    success_message = "Study design updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm
    template_name = "eco/design_update.html"

    def get_context_data(self, **kwargs):
        design_id = self.kwargs.pop("pk")
        context = super().get_context_data(**kwargs)
        study_id = self.object.study_id
        context["causes"] = models.Cause.objects.filter(study=study_id)
        context["effects"] = models.Effect.objects.filter(study=study_id)
        context["results"] = models.Result.objects.filter(design=design_id)
        return context


class DesignDetail(BaseDetail):
    model = models.Design
    template_name = "eco/design_detail.html"

    def get_context_data(self, **kwargs):
        design_id = self.kwargs.get("pk")
        context = super().get_context_data(**kwargs)
        study_id = self.object.study_id
        context["causes"] = models.Cause.objects.filter(study=study_id)
        context["effects"] = models.Effect.objects.filter(study=study_id)
        context["results"] = models.Result.objects.filter(design=design_id)
        return context


class DesignDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Design

    def get_context_data(self, **kwargs):
        design_id = self.kwargs.pop("pk")
        context = super().get_context_data(**kwargs)
        study_id = self.object.study_id
        context["causes"] = models.Cause.objects.filter(study=study_id)
        context["effects"] = models.Effect.objects.filter(study=study_id)
        context["results"] = models.Result.objects.filter(design=design_id)
        return context

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Design viewset
class DesignViewset(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Design
    form_fragment = "eco/fragments/_design_edit.html"
    detail_fragment = "eco/fragments/_design_table.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.DesignForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)


class DesignChildViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = None  # required
    form_class = None  # required
    form_fragment = "eco/fragments/_object_edit_row.html"
    detail_fragment = None  # required

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = self.form_class(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = self.form_class(parent=request.item.parent)
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": self.model.__name__.lower(), "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "eco/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        return context


# Result viewset
class ResultViewset(DesignChildViewset):
    model = models.Result
    form_class = forms.ResultForm
    parent_model = models.Design
    detail_fragment = "eco/fragments/result_row.html"


# Cause viewset
class CauseViewset(DesignChildViewset):
    model = models.Cause
    form_class = forms.CauseForm
    detail_fragment = "eco/fragments/cause_row.html"


# Effect viewset
class EffectViewset(DesignChildViewset):
    model = models.Effect
    form_class = forms.EffectForm
    detail_fragment = "eco/fragments/effect_row.html"
