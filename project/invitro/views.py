from assessment.models import Assessment
from utils.views import (
    BaseUpdate, BaseUpdateWithFormset
    GenerateReport, BaseList, BaseDetail, BaseCreate,
)

from study.models import Study
from . import models, forms, exports


class ExperimentCreate(BaseCreate):
    success_message = "Experiment created."
    parent_model = Study
    parent_template_name = 'study'
    model = models.IVExperiment
    form_class = forms.IVExperimentForm


class ExperimentDetail(BaseDetail):
    model = models.IVExperiment


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.IVExperiment
    form_class = forms.IVExperimentForm


class ChemicalCreate(BaseCreate):
    success_message = "Chemical created."
    parent_model = Study
    parent_template_name = 'study'
    model = models.IVChemical
    form_class = forms.IVChemicalForm


class ChemicalDetail(BaseDetail):
    model = models.IVChemical


class ChemicalUpdate(BaseUpdate):
    success_message = "Chemical updated."
    model = models.IVChemical
    form_class = forms.IVChemicalForm


class CellTypeCreate(BaseCreate):
    success_message = "Cell-type created."
    parent_model = Study
    parent_template_name = 'study'
    model = models.IVCellType
    form_class = forms.IVCellTypeForm


class CellTypeDetail(BaseDetail):
    model = models.IVCellType


class CellTypeUpdate(BaseUpdate):
    success_message = "Cell-type updated."
    model = models.IVCellType
    form_class = forms.IVCellTypeForm


class EndpointDetail(BaseDetail):
    model = models.IVEndpoint


class EndpointUpdate(BaseUpdateWithFormset):
    success_message = "Endpoint updated."
    model = models.IVEndpoint
    form_class = forms.IVEndpointForm
    formset_factory = forms.IVEndpointGroupFormset

    def build_initial_formset_factory(self):
        return forms.IVEndpointGroupFormset(
            queryset=self.object.groups.all().order_by('dose_group_id'))

    def post_object_save(self, form, formset):
        dose_group_id = 0
        for form in formset.forms:
            form.instance.endpoint = self.object
            if form.is_valid() and form not in formset.deleted_forms:
                form.instance.dose_group_id = dose_group_id
                if form.has_changed() is False:
                    form.instance.save()  # ensure new dose_group_id saved to db
                dose_group_id += 1


class EndpointsList(BaseList):
    parent_model = Assessment
    model = models.IVEndpoint

    def get_paginate_by(self, qs):
        val = 25
        try:
            val = int(self.request.GET.get('paginate_by', val))
        except ValueError:
            pass
        return val

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsList, self).get_obj_perms()
        if not perms['edit']:
            filters["experiment__study__published"] = True
        return self.model.objects.filter(**filters).order_by('name')


class EndpointsFullExport(EndpointsList):
    parent_model = Assessment
    model = models.IVEndpoint

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        export_format = request.GET.get("output", "excel")
        exporter = exports.DataPivotEndpoint(
            self.object_list,
            export_format=export_format,
            filename='{}-invitro'.format(self.assessment))
        return exporter.build_response()


class EndpointsReport(GenerateReport):
    parent_model = Assessment
    model = models.IVEndpoint
    report_type = 5

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsReport, self).get_obj_perms()
        if not perms['edit'] or self.onlyPublished:
            filters["experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "in-vitro.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(queryset)
