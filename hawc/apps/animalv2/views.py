import inspect

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
    FormsetConfiguration,
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

    # inline formsets - all optional
    formset_configurations = []

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        formsets = []
        formsets_valid_if_present = True
        if request.method == "POST":
            # make a copy; if we do any is_valid modifying of the data we need this...
            request.POST = request.POST.copy()

            form = self.form_class(request.POST, parent=request.item.parent)

            for formset_config in self.formset_configurations:
                formset = modelformset_factory(
                    formset_config.model_class,
                    form=formset_config.form_class,
                    can_delete=True,
                )(request.POST, prefix=formset_config.form_prefix)
                formsets.append(formset)

                if not formset.is_valid():
                    formsets_valid_if_present = False

            if form.is_valid() and formsets_valid_if_present:
                self.perform_create(request.item, form, formsets)
                template = self.detail_fragment
        else:
            form = self.form_class(parent=request.item.parent)
        context = self.get_context_data(form=form, formsets=formsets)
        return render(request, template, context)

    # TODO - update the update method
    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            # make a copy; if we do any is_valid modifying of the data we need this...
            request.POST = request.POST.copy()

        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)

        formsets = []
        formsets_valid_if_present = True

        if request.method == "POST" and form.is_valid():
            for formset_config in self.formset_configurations:
                formset = modelformset_factory(
                    formset_config.model_class,
                    form=formset_config.form_class,
                    can_delete=True,
                )(request.POST, prefix=formset_config.form_prefix)
                formsets.append(formset)

                if not formset.is_valid():
                    formsets_valid_if_present = False

            if formsets_valid_if_present:
                self.perform_update(request.item, form, formsets)
                template = self.detail_fragment
        context = self.get_context_data(form=form, formsets=formsets)
        return render(request, template, context)

    @transaction.atomic
    def perform_update(self, item: Item, form, formsets=[]):
        instance = form.save()
        create_object_log("Updated", instance, item.assessment.id, self.request.user.id)

        formset_idx = 0
        for formset in formsets:
            formset_config = self.formset_configurations[formset_idx]
            self.perform_formset_cud_operations(formset, formset_config, item.object)
            formset_idx += 1

    @transaction.atomic
    def perform_create(self, item: Item, form, formsets=[]):
        item.object = form.save()
        create_object_log("Created", item.object, item.assessment.id, self.request.user.id)

        formset_idx = 0
        for formset in formsets:
            formset_config = self.formset_configurations[formset_idx]
            self.perform_formset_cud_operations(formset, formset_config, item.object)
            formset_idx += 1

    def perform_formset_cud_operations(self, formset, formset_config, parent_obj_instance):
        # creates/updates/deletes instances represented in the sub formset; logs them; etc.
        temp_instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            create_object_log("Deleted", obj, obj.get_assessment().id, self.request.user.id)
            obj.delete()

        parent_key = formset_config.form_class.formset_parent_key
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

        formset_idx = 0
        formsets = kwargs.get("formsets", [])
        formset_contexts = []
        for formset_config in self.formset_configurations:
            formset = formsets[formset_idx] if formset_idx < len(formsets) else None

            if formset is None:
                formset = modelformset_factory(
                    formset_config.model_class,
                    form=formset_config.form_class,
                    can_delete=True,
                )(
                    # only show the subobjects related to this parent. The filter key is dynamic
                    # so we do it using a Q object.
                    #
                    # e.g. for DoseGroup editing we have a FormsetConfiguration "formset_config" where:
                    #       formset_config.form_class.formset_parent_key    == "treatment_id"
                    #       self.request.item.object.id                     == the id of the parent treatment
                    #       formset_config.sort_field                       == "dose_group_id"
                    #
                    # So this Q code is like doing:
                    #       queryset=formset_config.model_class.objects.filter(
                    #           treatment_id=x
                    #       ).order_by("dose_group_id")
                    queryset=formset_config.model_class.objects.filter(
                        Q(
                            (
                                formset_config.form_class.formset_parent_key,
                                self.request.item.object.id,
                            )
                        )
                    ).order_by(formset_config.sort_field)
                    if self.request.item.object is not None
                    else formset_config.model_class.objects.none(),
                    prefix=formset_config.form_prefix,
                )

            formset_contexts.append(
                {
                    "fragment": formset_config.fragment,
                    "instance": formset,
                    "helper": formset_config.helper_class(),
                }
            )
            formset_idx += 1

        context["formset_contexts"] = formset_contexts

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
    formset_configurations = [
        FormsetConfiguration(
            "animalv2/fragments/_treatment_formset.html",
            forms.DoseGroupForm,
            models.DoseGroup,
            forms.DoseGroupFormHelper,
            "dose_group_id",
            "dosegroupform",
        )
    ]


# Endpoint viewset
class EndpointViewSet(ExperimentChildViewSet):
    model = models.Endpoint
    form_class = forms.EndpointForm
    detail_fragment = "animalv2/fragments/_endpoint_row.html"


# ObservationTime viewset
class ObservationTimeViewSet(ExperimentChildViewSet):
    model = models.ObservationTime
    form_class = forms.ObservationTimeForm
    detail_fragment = "animalv2/fragments/_observationtime_row.html"


# DataExtraction viewset
class DataExtractionViewSet(ExperimentChildViewSet):
    model = models.DataExtraction
    form_class = forms.DataExtractionForm
    detail_fragment = "animalv2/fragments/_dataextraction_row.html"
    formset_configurations = [
        FormsetConfiguration(
            "animalv2/fragments/_dataextraction_formset_groupleveldata.html",
            forms.DoseResponseGroupLevelDataForm,
            models.DoseResponseGroupLevelData,
            forms.DoseResponseGroupLevelDataFormHelper,
            "id",
            "groupleveldataform",
        ),
        FormsetConfiguration(
            "animalv2/fragments/_dataextraction_formset_animalleveldata.html",
            forms.DoseResponseAnimalLevelDataForm,
            models.DoseResponseAnimalLevelData,
            forms.DoseResponseAnimalLevelDataFormHelper,
            "id",
            "animalleveldataform",
        ),
    ]
