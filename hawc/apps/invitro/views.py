from django.middleware.csrf import get_token
from django.urls import reverse

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig
from ..common.views import (
    BaseCreate,
    BaseCreateWithFormset,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseUpdate,
    BaseUpdateWithFormset,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from . import filterset, forms, models


# Experiment
class ExperimentCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Experiment created."
    parent_model = Study
    parent_template_name = "study"
    model = models.IVExperiment
    form_class = forms.IVExperimentForm


class ExperimentDetail(BaseDetail):
    model = models.IVExperiment


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.IVExperiment
    form_class = forms.IVExperimentForm


class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.IVExperiment

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Chemical
class ChemicalCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Chemical created."
    parent_model = Study
    parent_template_name = "study"
    model = models.IVChemical
    form_class = forms.IVChemicalForm


class ChemicalDetail(BaseDetail):
    model = models.IVChemical


class ChemicalUpdate(BaseUpdate):
    success_message = "Chemical updated."
    model = models.IVChemical
    form_class = forms.IVChemicalForm


class ChemicalDelete(BaseDelete):
    success_message = "Chemical deleted."
    model = models.IVChemical

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Cell type
class CellTypeCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Cell-type created."
    parent_model = Study
    parent_template_name = "study"
    model = models.IVCellType
    form_class = forms.IVCellTypeForm


class CellTypeDetail(BaseDetail):
    model = models.IVCellType


class CellTypeUpdate(BaseUpdate):
    success_message = "Cell-type updated."
    model = models.IVCellType
    form_class = forms.IVCellTypeForm


class CellTypeDelete(BaseDelete):
    success_message = "Cell-type deleted."
    model = models.IVCellType

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Endpoint categories
class EndpointCategoryUpdate(BaseDetail):
    model = Assessment
    template_name = "invitro/ivendpointecategory_form.html"
    assessment_permission = AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            breadcrumbs=[
                Breadcrumb.build_root(self.request.user),
                Breadcrumb.from_object(self.assessment),
                Breadcrumb(name="Update in-vitro endpoint categories"),
            ],
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        list_url = reverse("invitro:api:category-list") + f"?assessment_id={self.assessment.id}"
        return WebappConfig(
            app="nestedTagEditorStartup",
            data=dict(
                assessment_id=self.assessment.id,
                base_url=reverse("invitro:api:category-list"),
                list_url=list_url,
                csrf=get_token(self.request),
                host=f"//{self.request.get_host()}",
                title="Modify in-vitro endpoint categories",
                extraHelpHtml="",
                btnLabel="Add new category",
            ),
        )


# Endpoint
class EndpointCreate(BaseCreateWithFormset):
    success_message = "Endpoint created."
    parent_model = models.IVExperiment
    parent_template_name = "experiment"
    model = models.IVEndpoint
    form_class = forms.IVEndpointForm
    formset_factory = forms.IVEndpointGroupFormset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs

    def post_object_save(self, form, formset):
        dose_group_id = 0
        for form in formset.forms:
            if form in formset.extra_forms and not form.has_changed():
                continue  # skip unused extra forms in formset
            form.instance.endpoint = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.dose_group_id = dose_group_id
                if form.has_changed() is False:
                    form.instance.save()  # ensure new dose_group_id saved to db
                dose_group_id += 1

    def build_initial_formset_factory(self):
        return forms.BlankIVEndpointGroupFormset(queryset=models.IVEndpointGroup.objects.none())


class EndpointDetail(BaseDetail):
    model = models.IVEndpoint


class EndpointUpdate(BaseUpdateWithFormset):
    success_message = "Endpoint updated."
    model = models.IVEndpoint
    form_class = forms.IVEndpointForm
    formset_factory = forms.IVEndpointGroupFormset

    def build_initial_formset_factory(self):
        # make sure at least one group exists; we check because it's
        # possible to delete as well as create objects in this view.
        qs = self.object.groups.all().order_by("dose_group_id")
        fs = forms.IVEndpointGroupFormset(queryset=qs)
        if qs.count() == 0:
            fs.extra = 1
        return fs

    def post_object_save(self, form, formset):
        dose_group_id = 0
        for form in formset.forms:
            if form in formset.extra_forms and not form.has_changed():
                continue  # skip unused extra forms in formset
            form.instance.endpoint = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.dose_group_id = dose_group_id
                if form.has_changed() is False:
                    form.instance.save()  # ensure new dose_group_id saved to db
                dose_group_id += 1

        benchmark_formset = forms.IVBenchmarkFormset(self.request.POST, instance=self.object)
        if benchmark_formset.is_valid():
            benchmark_formset.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["benchmark_formset"] = forms.IVBenchmarkFormset(instance=self.object)
        return context


class EndpointDelete(BaseDelete):
    success_message = "Endpoint deleted."
    model = models.IVEndpoint

    def get_success_url(self):
        return self.object.experiment.get_absolute_url()


class EndpointFilterList(BaseFilterList):
    parent_model = Assessment
    model = models.IVEndpoint
    filterset_class = filterset.EndpointFilterSet

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("experiment__study", "experiment__dose_units", "chemical")
            .prefetch_related("effects")
        )
