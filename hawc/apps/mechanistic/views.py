from django.http import HttpRequest
from django.shortcuts import render

from ..assessment.models import TimeSpentEditing
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


class ExperimentCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Experiment created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Experiment
    form_class = forms.ExperimentForm

    def get_success_url(self):
        super().get_success_url()
        return self.object.get_update_url()


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Experiment
    form_class = forms.ExperimentForm
    template_name = "mechanistic/experiment_update.html"

    """
    def get_queryset(self):
        return super().get_queryset().complete()
    """


class ExperimentDetail(BaseDetail):
    model = models.Experiment

    """
    def get_queryset(self):
        return super().get_queryset().complete()
    """


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
    form_fragment = "mechanistic/fragments/_experiment_edit.html"
    detail_fragment = "mechanistic/fragments/_experiment_table.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.ExperimentForm(data=data, instance=request.item.object)
        if request.method == "GET":
            TimeSpentEditing.set_start_time(request)
        elif request.method == "POST" and form.is_valid():
            TimeSpentEditing.add_time_spent_job(
                request, request.item.object, request.item.assessment.id
            )
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

