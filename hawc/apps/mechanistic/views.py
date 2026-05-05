from django.http import HttpRequest
from django.shortcuts import render

from ..assessment.models import TimeSpentEditing
from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCopyForm,
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


class ExperimentCopyForm(BaseCopyForm):
    copy_model = models.Experiment
    form_class = forms.ExperimentSelectorForm
    model = Study


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

        # prepopulate it with data from the Experiment...this is kind of weird. If you instantiate the form like this:
        #
        #       form = forms.ExperimentForm(data=data, instance=request.item.object)
        #
        # you don't need to set data like this; django/crispy must use the instance to prepopulate fields. But, if
        # you instantiate the form like this:
        #
        #       form = forms.ExperimentForm(data=data, instance=request.item.object, files=request.FILES)
        #
        # (which we have to do, since Experiment has a FileField for protocol), then the form will render initially
        # with no existing data filled in (i.e., the "name" field doesn't have the model.name filled in to start!
        #
        # I spent an *extremely* long time trying to figure out why and eventually settled on this as the fix. Is something
        # weird with the crispy setup? With the model/view? Is htmx confusing things? I give up, this works. -tfeiler 20260417
        if data is None:
            obj = request.item.object
            data = {
                "name": obj.name,
                "description": obj.description,
                "test_facility": obj.test_facility,
                "guideline": obj.guideline,
                "guideline_name_number": obj.guideline_name_number,
                "guideline_compliance": obj.guideline_compliance,
            }

        # useful reading:
        # https://www.reddit.com/r/django/comments/b2xn3l/requestfiles_is_empty_file_didnt_upload/
        # https://stackoverflow.com/questions/680770/django-imagefield-not-working-properly-via-modelform/681657#681657
        # https://stackoverflow.com/questions/7920128/what-is-the-difference-between-initial-data-and-bound-data-django-forms
        form = forms.ExperimentForm(data=data, instance=request.item.object, files=request.FILES)
        # form = forms.ExperimentForm(data=data, instance=request.item.object)

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


class ExperimentChildViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Experiment
    model = None  # required
    form_class = None  # required
    form_fragment = "common/fragments/_object_edit_row.html"
    detail_fragment = None  # required

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "GET":
            form = self.form_class(parent=request.item.parent)
            TimeSpentEditing.set_start_time(request)
        else:
            form = self.form_class(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
                TimeSpentEditing.add_time_spent_job(
                    request, request.item.object, request.item.assessment.id
                )
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)
        if request.method == "GET":
            TimeSpentEditing.set_start_time(request)
        elif request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
            TimeSpentEditing.add_time_spent_job(
                request, request.item.object, request.item.assessment.id
            )
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": self.model.__name__.lower(), "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "common/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        context["app"] = "mechanistic"
        return context


class ChemicalCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Chemical created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Chemical
    form_class = forms.ChemicalForm

    def get_success_url(self):
        super().get_success_url()
        return self.object.get_update_url()


class ChemicalUpdate(BaseUpdate):
    success_message = "Chemical updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Chemical
    form_class = forms.ChemicalForm
    # template_name = "mechanistic/chemical_update.html"


class ChemicalDetail(BaseDetail):
    model = models.Chemical


class ChemicalDelete(BaseDelete):
    success_message = "Chemical deleted."
    model = models.Chemical

    def get_success_url(self):
        return self.object.study.get_absolute_url()


class ChemicalCopyForm(BaseCopyForm):
    copy_model = models.Chemical
    form_class = forms.ChemicalSelectorForm
    model = Study


# REMOVE NOW TAHT CHEMICALS ARE NOT AN EXPERIMENT SUBOBJ???
# Chemical viewset
"""
class ChemicalViewSet(ExperimentChildViewSet):
    model = models.Chemical
    form_class = forms.ChemicalForm
    detail_fragment = "mechanistic/fragments/chemical_row.html"
"""


class TestSystemViewSet(ExperimentChildViewSet):
    model = models.TestSystem
    form_class = forms.TestSystemForm
    detail_fragment = "mechanistic/fragments/testsystem_row.html"


class MethodViewSet(ExperimentChildViewSet):
    model = models.Method
    form_class = forms.MethodForm
    detail_fragment = "mechanistic/fragments/method_row.html"
