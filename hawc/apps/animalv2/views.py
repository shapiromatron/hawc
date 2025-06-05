from django.db import transaction
from django.db.models import Model, Q
from django.forms import BaseForm, modelformset_factory
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from ..assessment.models import Assessment
from ..common.forms import FormsetGenericFormHelper
from ..common.htmx import HtmxViewSet, Item, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    FormsetConfiguration,
    create_object_log,
)
from ..mgmt.constants import TaskType
from ..mgmt.models import Task
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from ..vocab.models import GuidelineProfile
from . import filterset, forms, models

# TODO - make sure HTML views efficiently query database, HTMX views lower priority


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


class ExperimentDetail(BaseDetail):
    model = models.Experiment


class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.Experiment

    def get_success_url(self):
        return self.object.study.get_absolute_url()


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
    model: type[Model]
    form_class: type[BaseForm]
    form_fragment = "common/fragments/_object_edit_row.html"
    detail_fragment: str
    formset_configurations = []

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        formsets = []
        formsets_valid_if_present = True
        # TODO - refactor shared code between `create` and `update`?
        # TODO - errors in formset forms not rendering - show?
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
    def perform_update(self, item: Item, form, formsets=None):
        if formsets is None:
            formsets = []

        instance = form.save()
        create_object_log("Updated", instance, item.assessment.id, self.request.user.id)

        formset_idx = 0
        for formset in formsets:
            formset_config = self.formset_configurations[formset_idx]
            self.perform_formset_cud_operations(formset, formset_config, item.object)
            formset_idx += 1

    @transaction.atomic
    def perform_create(self, item: Item, form, formsets=None):
        if formsets is None:
            formsets = []

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
            return render(request, "common/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        context["app"] = "animalv2"

        formsets = kwargs.get("formsets", [])
        formsets = []
        for formset_idx, formset_config in enumerate(self.formset_configurations):
            formset = formsets[formset_idx] if formset_idx < len(formsets) else None

            if formset is None:
                formset = modelformset_factory(
                    formset_config.model_class,
                    form=formset_config.form_class,
                    can_delete=True,
                )(
                    # only show the subobjects related to this parent.
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

            formsets.append(
                {
                    "fragment": formset_config.template,
                    "instance": formset,
                    "helper": formset_config.helper_class(),
                }
            )

        context["formsets"] = formsets

        return context


class ExperimentFilterList(BaseFilterList):
    template_name = "animalv2/experiment_list.html"
    parent_model = Assessment
    model = models.Experiment
    filterset_class = filterset.ExperimentFilterSet
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset()


class ChemicalViewSet(ExperimentChildViewSet):
    model = models.Chemical
    form_class = forms.ChemicalForm
    detail_fragment = "animalv2/fragments/_chemical_row.html"


class AnimalGroupViewSet(ExperimentChildViewSet):
    model = models.AnimalGroup
    form_class = forms.AnimalGroupForm
    detail_fragment = "animalv2/fragments/_animalgroup_row.html"


class TreatmentViewSet(ExperimentChildViewSet):
    model = models.Treatment
    form_class = forms.TreatmentForm
    detail_fragment = "animalv2/fragments/_treatment_row.html"
    formset_configurations = [
        FormsetConfiguration(
            models.DoseGroup,
            forms.DoseGroupForm,
            FormsetGenericFormHelper,
            "dosegroupform",
            "dose_group_id",
            "animalv2/fragments/_treatment_formset.html",
        )
    ]


class EndpointViewSet(ExperimentChildViewSet):
    model = models.Endpoint
    form_class = forms.EndpointForm
    detail_fragment = "animalv2/fragments/_endpoint_row.html"


class ObservationTimeViewSet(ExperimentChildViewSet):
    model = models.ObservationTime
    form_class = forms.ObservationTimeForm
    detail_fragment = "animalv2/fragments/_observationtime_row.html"


class DataExtractionViewSet(ExperimentChildViewSet):
    model = models.DataExtraction
    form_class = forms.DataExtractionForm
    detail_fragment = "animalv2/fragments/_dataextraction_row.html"
    formset_configurations = [
        FormsetConfiguration(
            models.DoseResponseGroupLevelData,
            forms.DoseResponseGroupLevelDataForm,
            FormsetGenericFormHelper,
            "groupleveldataform",
            "id",
            "animalv2/fragments/_dataextraction_formset_groupleveldata.html",
        ),
        FormsetConfiguration(
            models.DoseResponseAnimalLevelData,
            forms.DoseResponseAnimalLevelDataForm,
            FormsetGenericFormHelper,
            "animalleveldataform",
            "id",
            "animalv2/fragments/_dataextraction_formset_animalleveldata.html",
        ),
    ]


class StudyLevelValues(BaseList):
    parent_model = Study
    model = models.StudyLevelValue
    template_name = "animalv2/studylevelvalues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(study=self.parent)
        return context

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(study=self.parent)
            .select_related("units")
            .order_by("-created")
        )
        return queryset


class StudyLevelValueViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Study
    model = models.StudyLevelValue

    form_fragment = "animalv2/fragments/studylevelvalue_edit_row.html"
    detail_fragment = "animalv2/fragments/studylevelvalue_row.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
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
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = forms.StudyLevelValueForm(data=form_data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        form = forms.StudyLevelValueForm(data=None, instance=request.item.object)
        context = self.get_context_data(form=form)
        return render(request, self.detail_fragment, context)


class ObservationList(BaseFilterList):
    parent_model = models.Experiment
    model = models.Observation
    filterset_class = filterset.ObservationFilterSet
    template_name = "animalv2/observation_details.html"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().filter(experiment_id=self.parent.id)
        if self.parent.guideline:
            observations = self.generate_observations(list(qs))
            return self.filterset_class.filter(self, observations)
        else:
            return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment = self.parent
        data_extracted = Task.objects.filter(study_id=experiment.study.id, type=TaskType.EXTRACTION)
        context["guideline"] = self.parent.guideline
        context["data_extraction"] = data_extracted.first()
        context["experiment"] = experiment.id
        context["assessment"] = self.parent.get_assessment()
        return context

    def generate_observations(self, observations):
        # Get all GP instances pertaining to toxrefdb
        guideline_id = GuidelineProfile.objects.get_guideline_id(self.parent.guideline)
        profiles = GuidelineProfile.objects.filter(
            guideline_id=guideline_id,
        ).select_related("endpoint__parent", "endpoint__parent__parent")

        # get all endpoints
        term_ids = [profile.endpoint.id for profile in profiles]
        endpoints = models.Endpoint.objects.filter(effect_subtype_term_id__in=term_ids)
        endpoint_dict = {e.effect_subtype_term_id: e for e in endpoints}

        # add saved observations
        data = []
        stored_endpoints = []
        for item in observations:
            item.endpoints = endpoint_dict.get(item.endpoint.id)
            data.append(item)
            stored_endpoints.append(item.endpoint)

        # generate new observations
        for profile in profiles:
            endpoint = profile.endpoint
            if endpoint not in stored_endpoints:
                endpoint_data = endpoint_dict.get(endpoint.id)
                observation = self.model.objects.default_observation(profile, endpoint_data)
                # get term inheritance
                observation.endpoints = endpoint_data
                data.append(observation)
        return data


class ObservationViewSet(HtmxViewSet):
    actions = {"create", "update"}
    parent_model = models.Experiment
    model = models.Observation
    form_fragment = "animalv2/fragments/observation_form.html"
    detail_fragment = "animalv2/observation_detail.html"

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            endpoint_id = self.request.GET.get("endpoint")
            instance = self.model.objects.filter(
                experiment=request.item.parent, endpoint=endpoint_id
            ).first()

            if instance:
                self.perform_update(request, instance, "Update", kwargs["status"])
            else:
                term = get_object_or_404(models.Term, pk=endpoint_id)
                instance = models.Observation(endpoint=term, experiment=request.item.parent)
                self.perform_update(request, instance, "Create", kwargs["status"])
        return render(
            request, self.form_fragment, self.get_context_data(instance, request, kwargs["status"])
        )

    @transaction.atomic
    def perform_update(self, request, instance, action, status):
        checkbox = f"{instance.endpoint.id}-{status}"
        # An experiment must have a guideline to have observations
        if not instance.experiment.guideline:
            return

        # Get default statuses for an object
        guideline_id = GuidelineProfile.objects.get_guideline_id(instance.experiment.guideline)

        profile = GuidelineProfile.objects.filter(
            guideline_id=guideline_id, endpoint_id=instance.endpoint.id
        ).first()
        endpoint = models.Endpoint.objects.filter(
            effect_subtype_term_id=instance.endpoint.id
        ).first()
        default = self.model.objects.default_observation(profile, endpoint)

        # Set default attributes or update
        if action == "Create":
            instance.tested_status = default.tested_status
            instance.reported_status = default.reported_status

        if status == "tested_status":
            instance.tested_status = request.POST.get(checkbox) != "True"
        else:
            instance.reported_status = request.POST.get(checkbox) != "True"

        if action == "Update" and self.default_statuses(instance, default):
            instance.delete()
        else:
            instance.save()
            create_object_log(action, instance, request.item.assessment.id, request.user.id)

    def default_statuses(self, instance, default):
        if (
            instance.tested_status == default.tested_status
            and instance.reported_status == default.reported_status
        ):
            return True
        return False

    def get_context_data(self, instance, request, status, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = instance
        context["status"] = status
        context["experiment"] = instance.experiment.id
        context["assessment"] = request.item.assessment.id
        return context
