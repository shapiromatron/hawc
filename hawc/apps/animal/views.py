import json

from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator

from ..assessment.models import Assessment, DoseUnits
from ..common.forms import form_error_lis_to_ul, form_error_list_to_lis
from ..common.helper import WebappConfig
from ..common.views import (
    BaseCreate,
    BaseCreateWithFormset,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseList,
    BaseUpdate,
    BaseUpdateWithFormset,
    CopyAsNewSelectorMixin,
    HeatmapBase,
    beta_tester_required,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from ..study.views import StudyDetail
from ..udf.views import UDFDetailMixin
from . import filterset, forms, models


# Heatmap views
class HeatmapStudyDesign(HeatmapBase):
    heatmap_data_class = "bioassay-study-design"
    heatmap_data_url = "animal:api:assessment-study-heatmap"
    heatmap_view_title = "Bioassay study design summary"


class HeatmapEndpoint(HeatmapBase):
    heatmap_data_class = "bioassay-endpoint-summary"
    heatmap_data_url = "animal:api:assessment-endpoint-heatmap"
    heatmap_view_title = "Bioassay endpoint heatmap summary"


class HeatmapEndpointDose(HeatmapBase):
    heatmap_data_class = "bioassay-endpoint-doses-summary"
    heatmap_data_url = "animal:api:assessment-endpoint-doses-heatmap"
    heatmap_view_title = "Bioassay endpoint + doses heatmap summary"


# Experiment Views
class ExperimentCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Experiment created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Experiment
    form_class = forms.ExperimentForm


class ExperimentDetail(BaseDetail):
    model = models.Experiment


class ExperimentCopyAsNewSelector(CopyAsNewSelectorMixin, StudyDetail):
    copy_model = models.Experiment
    form_class = forms.ExperimentSelectorForm


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.Experiment
    form_class = forms.ExperimentForm


class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.Experiment

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Animal Group Views
class AnimalGroupCreate(BaseCreate):
    # Create view of AnimalGroup, and sometimes DosingRegime if generational.
    model = models.AnimalGroup
    parent_model = models.Experiment
    parent_template_name = "experiment"
    template_name = "animal/animalgroup_form.html"
    success_message = "Animal Group created."
    crud = "Create"

    def get_form_class(self):
        self.is_generational = self.parent.is_generational()
        return forms.GenerationalAnimalGroupForm if self.is_generational else forms.AnimalGroupForm

    @transaction.atomic
    def form_valid(self, form):
        """
        Save form, and perhaps dosing regime and dosing groups, if appropriate.

        If an animal group is NOT generational, then it requires its own dosing
        regime. Thus, we must make sure the dosing regime is valid before
        attempting to save. If an animal group IS generational, a dosing-regime
        can be specified from parent groups. OR, a dosing-regime can be created.
        """
        self.object = form.save(commit=False)

        # If a dosing-regime is already specified, save as normal
        if self.is_generational and self.object.dosing_regime:
            return super().form_valid(form)

        # Otherwise we create a new dosing-regime, as well as the associated
        # dose-groups using a formset.
        self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST)
        if self.form_dosing_regime.is_valid():
            dosing_regime = self.form_dosing_regime.save(commit=False)

            # unpack dose-groups into formset and validate
            # occasionally POST['dose_groups_json'] will be '', which json.loads
            # will raise an error on. Replace with '{}' on those occasions.
            dose_groups = self.request.POST["dose_groups_json"]
            dose_groups_json = dose_groups if dose_groups != "" else "{}"
            fs_initial = json.loads(dose_groups_json)
            fs = forms.dosegroup_formset_factory(fs_initial, dosing_regime.num_dose_groups)

            if fs.is_valid():
                # save dosing-regime and associate animal-group,
                # setting foreign-key interrelationships
                dosing_regime.save()
                self.object.dosing_regime = dosing_regime
                self.object.save()
                dosing_regime.dosed_animals = self.object
                dosing_regime.save()
                self.create_log(dosing_regime)

                # now save dose-groups, one for each dosing regime
                for dose in fs.forms:
                    dose.instance.dose_regime = dosing_regime

                fs.save()

                return super().form_valid(form)

            else:
                # invalid formset; extract formset errors
                lis = []
                for f in fs.forms:
                    if len(list(f.errors.keys())) > 0:
                        lis.extend(form_error_list_to_lis(f))
                if len(fs._non_form_errors) > 0:
                    lis.extend(fs._non_form_errors)
                self.dose_groups_errors = form_error_lis_to_ul(lis)
                return self.form_invalid(form)
        else:
            # invalid dosing-regime
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()
        if hasattr(self, "form_dosing_regime"):
            context["form_dosing_regime"] = self.form_dosing_regime
        else:
            context["form_dosing_regime"] = forms.DosingRegimeForm()

        if self.request.method == "POST":  # send back dose-group errors
            context["dose_groups_json"] = self.request.POST["dose_groups_json"]
            if hasattr(self, "dose_groups_errors"):
                context["dose_groups_errors"] = self.dose_groups_errors

        return context


class AnimalGroupDetail(BaseDetail):
    model = models.AnimalGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        endpoints = (
            self.object.endpoints.all()
            .select_related(
                "assessment",
                "animal_group__experiment__dtxsid",
                "animal_group__experiment__study",
                "animal_group__species",
                "animal_group__strain",
            )
            .prefetch_related(
                "bmd_sessions",
                "effects",
                "groups",
                "animal_group__parents",
                "animal_group__siblings",
                "animal_group__children",
                "animal_group__dosing_regime__doses__dose_units",
                "animal_group__experiment__study__searches",
                "animal_group__experiment__study__identifiers",
            )
        )
        context["config"] = dict(
            id=self.object.id,
            has_dosing_regime=self.object.dosing_regime is not None,
            endpoints=[endpoint.get_json(json_encode=False) for endpoint in endpoints],
        )
        return context


class AnimalGroupCopyAsNewSelector(CopyAsNewSelectorMixin, ExperimentDetail):
    copy_model = models.AnimalGroup
    form_class = forms.AnimalGroupSelectorForm


class AnimalGroupUpdate(BaseUpdate):
    """
    Update selected animal-group. Dosing regime cannot be edited.
    """

    model = models.AnimalGroup
    template_name = "animal/animalgroup_form.html"
    form_class = forms.AnimalGroupForm
    success_message = "Animal Group updated."

    def get_object(self, queryset=None):
        obj = super().get_object()
        self.dosing_regime = obj.dosing_regime
        if obj.is_generational:
            self.form_class = forms.GenerationalAnimalGroupForm
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()
        return context


class AnimalGroupDelete(BaseDelete):
    success_message = "Animal-group deleted."
    model = models.AnimalGroup

    def get_success_url(self):
        if not self.object.can_delete():
            raise ValueError("Cannot be deleted")
        return self.object.experiment.get_absolute_url()


class EndpointCopyAsNewSelector(CopyAsNewSelectorMixin, AnimalGroupDetail):
    copy_model = models.Endpoint
    form_class = forms.EndpointSelectorForm

    def get_related_id(self):
        return self.object.experiment.study_id


# Dosing Regime Views
class DosingRegimeUpdate(BaseUpdate):
    """
    Update selected dosing regime. Has custom logic to also add dose-groups with
    each creation of a dose-regime.
    """

    model = models.DosingRegime
    form_class = forms.DosingRegimeForm
    success_message = "Dosing regime updated."

    @transaction.atomic
    def form_valid(self, form):
        """
        If the dosing-regime is valid, then check if the formset is valid. If
        it is, then continue saving.
        """
        self.object = form.save(commit=False)

        # unpack dose-groups into formset and validate
        fs_initial = json.loads(self.request.POST["dose_groups_json"])
        fs = forms.dosegroup_formset_factory(fs_initial, self.object.num_dose_groups)

        if fs.is_valid():
            # instead of checking existing vs. new, just delete all old
            # dose-groups, and save new formset
            models.DoseGroup.objects.by_dose_regime(self.object).delete()

            # now save dose-groups, one for each dosing regime
            for dose in fs.forms:
                dose.instance.dose_regime = self.object

            fs.save()

            return super().form_valid(form)

        else:
            # invalid formset; extract formset errors
            lis = []
            for f in fs.forms:
                if len(list(f.errors.keys())) > 0:
                    lis.extend(form_error_list_to_lis(f))
            if len(fs._non_form_errors) > 0:
                lis.extend(fs._non_form_errors)
            self.dose_groups_errors = form_error_lis_to_ul(lis)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()

        if self.request.method == "POST":  # send back dose-group errors
            context["dose_groups_json"] = self.request.POST["dose_groups_json"]
            if hasattr(self, "dose_groups_errors"):
                context["dose_groups_errors"] = self.dose_groups_errors
        else:
            context["dose_groups_json"] = json.dumps(
                list(self.object.doses.values("dose", "dose_group_id", "dose_units"))
            )

        return context

    def get_success_url(self):
        super().get_success_url()
        return self.object.dosed_animals.get_absolute_url()


# Endpoint Views
class EndpointCreate(BaseCreateWithFormset):
    success_message = "Assessed-outcome created."
    parent_model = models.AnimalGroup
    parent_template_name = "animal_group"
    model = models.Endpoint
    form_class = forms.EndpointForm
    formset_factory = forms.EndpointGroupFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs

    def build_initial_formset_factory(self):
        num_groups = self.parent.dosing_regime.num_dose_groups if self.parent.dosing_regime else 1
        Formset = modelformset_factory(
            models.EndpointGroup,
            form=forms.EndpointGroupForm,
            formset=forms.BaseEndpointGroupFormSet,
            extra=num_groups,
        )
        return Formset(queryset=models.EndpointGroup.objects.none())

    def pre_validate(self, form, formset):
        # required for dataset-type checks
        for egform in formset.forms:
            egform.endpoint_form = form

    @transaction.atomic
    def form_valid(self, form, formset):
        self.object = form.save()
        if self.object.dose_response_available:
            self.post_object_save(form, formset)
            for egform in formset.forms:
                # save all EGs, even if no data
                egform.save()
            self.post_formset_save(form, formset)
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def post_object_save(self, form, formset):
        for i, egform in enumerate(formset.forms):
            egform.instance.endpoint = self.object
            egform.instance.dose_group_id = i

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["animal_group"] = self.parent
        context["vocabulary"] = self.model.get_vocabulary_settings(self.assessment, context["form"])
        return context


class EndpointUpdate(BaseUpdateWithFormset):
    success_message = "Endpoint updated."
    model = models.Endpoint
    form_class = forms.EndpointForm
    formset_factory = forms.EndpointGroupFormSet

    def build_initial_formset_factory(self):
        return forms.EndpointGroupFormSet(queryset=self.object.groups.all())

    def pre_validate(self, form, formset):
        for egform in formset.forms:
            egform.endpoint_form = form

    @transaction.atomic
    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        for egform in formset.forms:
            # save all EGs, even if no data
            egform.save()
        self.post_formset_save(form, formset)
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["animal_group"] = self.object.animal_group
        context["vocabulary"] = self.model.get_vocabulary_settings(self.assessment, context["form"])
        return context


class EndpointFilterList(BaseFilterList):
    parent_model = Assessment
    model = models.Endpoint
    filterset_class = filterset.EndpointFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        form = self.filterset.form
        dose_units = (
            form.cleaned_data.get("dose_units") or form.fields["dose_units"].queryset.first()
        )
        return qs.select_related("animal_group__experiment__study").annotate_dose_values(dose_units)

    def get_context_data(self, **kwargs):
        oel_names = self.assessment.get_noel_names()
        header_names = f"Study,Experiment,Animal group,Endpoint,Units,{oel_names.noel},{oel_names.loel},BMD,BMDL"
        kwargs.update(header_names=header_names)
        return super().get_context_data(**kwargs)


@method_decorator(beta_tester_required, name="dispatch")
class EndpointListV2(BaseList):
    parent_model = Assessment
    model = models.Endpoint
    template_name = "animal/endpoint_list_v2.html"

    def get_app_config(self, context) -> WebappConfig:
        url = reverse("animal:api:assessment-endpoints", args=(self.assessment.id,))
        if self.request.GET.get("unpublished", "false").lower() == "true":
            url += "?unpublished=true"
        return WebappConfig(
            app="animalStartup", page="startupEndpointListApp", data=dict(data_url=url)
        )


class EndpointDetail(UDFDetailMixin, BaseDetail):
    model = models.Endpoint
    queryset = models.Endpoint.objects.select_related(
        "animal_group",
        "animal_group__dosing_regime",
        "animal_group__experiment",
        "animal_group__experiment__study",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bmd_session"] = self.object.get_latest_bmd_session()
        return context


class EndpointDelete(BaseDelete):
    success_message = "Endpoint deleted."
    model = models.Endpoint

    def get_success_url(self):
        return self.object.animal_group.get_absolute_url()
