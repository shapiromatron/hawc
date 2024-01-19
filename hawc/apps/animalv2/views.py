from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseUpdate,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from . import forms, models


# Experiment Views
class ExperimentCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Experiment created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Experiment
    form_class = forms.ExperimentForm


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Experiment
    form_class = forms.ExperimentForm
    template_name = "animalv2/experiment_update.html"

    # currently just using default behavior; once I am making sub-objects (animalgroups, treatments,
    # etc.) then revisit ExperimentManager to do some smart prefetching. See
    # epiv2/managers.py::DesignManager for an example of this in use.
    # ExperimentDelete has a similarly commented-out overridden get_queryset...
    """
    def get_queryset(self):
        return super().get_queryset().complete()
    """


class ExperimentDetail(BaseDetail):
    model = models.Experiment


class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.Experiment

    """
    def get_queryset(self):
        return super().get_queryset().complete()
    """

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Experiment viewset
class ExperimentViewSet(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Experiment
    form_fragment = "animalv2/fragments/_experiment_edit.html"
    detail_fragment = "animalv2/fragments/_experiment_table.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.ExperimentForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)


class ExperimentChildViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Experiment
    model = None  # required
    form_class = None  # required
    form_fragment = "animalv2/fragments/_object_edit_row.html"
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
            context = {
                "attribute": self.model.__name__.lower(),
                "id": request.item.object.id,
            }
            self.perform_delete(request.item)
            return render(request, "animalv2/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        return context


# Chemical viewset
class ChemicalViewSet(ExperimentChildViewSet):
    model = models.Chemical
    form_class = forms.ChemicalForm
    detail_fragment = "animalv2/fragments/_chemical_row.html"
