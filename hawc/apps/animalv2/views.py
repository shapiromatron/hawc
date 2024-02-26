from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpRequest
from django.shortcuts import render

from ..common.htmx import HtmxViewSet, Item, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseUpdate,
    create_object_log,
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

    # inline formset - all optional
    formset_fragment = None
    formset_form_class = None
    formset_model_class = None
    formset_helper_class = None

    def supports_formset(self) -> bool:
        return (
            self.formset_fragment is not None
            and self.formset_form_class is not None
            and self.formset_model_class is not None
            and self.formset_helper_class is not None
        )

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        formset = None
        if request.method == "POST":
            form = self.form_class(request.POST, parent=request.item.parent)

            formset = None
            if self.supports_formset():
                formset = modelformset_factory(
                    self.formset_model_class,
                    form=self.formset_form_class,
                    can_delete=True,
                )(request.POST)

            if form.is_valid() and (formset is None or formset.is_valid()):
                self.perform_create(request.item, form, formset)
                template = self.detail_fragment
        else:
            form = self.form_class(parent=request.item.parent)
        context = self.get_context_data(form=form, formset=formset)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)

        formset = None

        if request.method == "POST" and form.is_valid():
            if self.supports_formset():
                formset = modelformset_factory(
                    self.formset_model_class,
                    form=self.formset_form_class,
                    can_delete=True,
                )(request.POST)
            if formset is None or formset.is_valid():
                self.perform_update(request.item, form, formset)
                template = self.detail_fragment
        context = self.get_context_data(form=form, formset=formset)
        return render(request, template, context)

    @transaction.atomic
    def perform_update(self, item: Item, form, formset=None):
        instance = form.save()
        create_object_log("Updated", instance, item.assessment.id, self.request.user.id)

        if formset is not None:
            self.perform_formset_cud_operations(formset, instance)

    @transaction.atomic
    def perform_create(self, item: Item, form, formset=None):
        item.object = form.save()
        create_object_log("Created", item.object, item.assessment.id, self.request.user.id)

        if formset is not None:
            self.perform_formset_cud_operations(formset, item.object)

    def perform_formset_cud_operations(self, formset, parent_obj_instance):
        # creates/updates/deletes instances represented in the sub formset; logs them; etc.
        temp_instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            create_object_log("Deleted", obj, obj.get_assessment().id, self.request.user.id)
            obj.delete()

        parent_key = self.formset_form_class.formset_parent_key
        for temp_instance in temp_instances:
            setattr(temp_instance, parent_key, parent_obj_instance.id)
            is_create = temp_instance.id is None
            temp_instance.save()

            create_object_log(
                "Created" if is_create else "Updated",
                temp_instance,
                temp_instance.get_assessment().id,
                self.request.user.id,
            )

    # data = self.request.POST if self.request.method == "POST" else None
    # print(f"perform_update; data is '{data}'")

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
        if self.supports_formset():
            context["formset_template_fragment"] = self.formset_fragment

            # if we can, use the previous formset to avoid losing in-progress edits, display errors, etc.
            formset = kwargs.get("formset")
            if formset is None:
                formset = modelformset_factory(
                    self.formset_model_class,
                    form=self.formset_form_class,
                    can_delete=True,
                )(
                    # only show the subobjects related to this parent. The filter key is dynamic
                    # so we do it using a Q object.
                    #
                    # e.g. for DoseGroup editing:
                    #       self.formset_form_class.formset_parent_key is "treatment_id"
                    #       self.request.item.object.id is the id of the parent treatment
                    #
                    # So this Q code is like doing:
                    #       queryset=self.formset_model_class.objects.filter(
                    #           treatment_id=x
                    #       ).order_by("dose_group_id")
                    queryset=self.formset_model_class.objects.filter(
                        Q(
                            (
                                self.formset_form_class.formset_parent_key,
                                self.request.item.object.id,
                            )
                        )
                    ).order_by("dose_group_id")
                    if self.request.item.object is not None
                    else self.formset_model_class.objects.none()
                )
            context["formset_instance"] = formset
            context["formset_helper"] = self.formset_helper_class()
        return context


# Chemical viewset
class ChemicalViewSet(ExperimentChildViewSet):
    model = models.Chemical
    form_class = forms.ChemicalForm
    detail_fragment = "animalv2/fragments/_chemical_row.html"


# AnimalGroup viewset
class AnimalGroupViewSet(ExperimentChildViewSet):
    model = models.AnimalGroup
    form_class = forms.AnimalGroupForm
    detail_fragment = "animalv2/fragments/_animalgroup_row.html"


# Treatment viewset
class TreatmentViewSet(ExperimentChildViewSet):
    model = models.Treatment
    form_class = forms.TreatmentForm
    detail_fragment = "animalv2/fragments/_treatment_row.html"
    formset_fragment = "animalv2/fragments/_treatment_formset.html"
    formset_form_class = forms.DoseGroupForm
    formset_model_class = models.DoseGroup
    formset_helper_class = forms.DoseGroupFormHelper


# Endpoint viewset
class EndpointViewSet(ExperimentChildViewSet):
    model = models.Endpoint
    form_class = forms.EndpointForm
    detail_fragment = "animalv2/fragments/_endpoint_row.html"


# ObservationTim viewset
class ObservationTimeViewSet(ExperimentChildViewSet):
    model = models.ObservationTime
    form_class = forms.ObservationTimeForm
    detail_fragment = "animalv2/fragments/_observationtime_row.html"
