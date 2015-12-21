from assessment.models import Assessment
from utils.views import GenerateReport, BaseList, BaseDetail, BaseUpdate

from . import models, forms, exports


class ExperimentDetail(BaseDetail):
    model = models.IVExperiment


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.IVExperiment
    form_class = forms.IVExperimentForm


class ChemicalDetail(BaseDetail):
    model = models.IVChemical


class ChemicalUpdate(BaseUpdate):
    success_message = "Chemical updated."
    model = models.IVChemical
    form_class = forms.IVChemicalForm


class CellTypeDetail(BaseDetail):
    model = models.IVCellType


class CellTypeUpdate(BaseUpdate):
    success_message = "Cell-type updated."
    model = models.IVCellType
    form_class = forms.IVCellTypeForm


class EndpointDetail(BaseDetail):
    model = models.IVEndpoint


class EndpointUpdate(BaseUpdate):
    success_message = "Endpoint updated."
    model = models.IVEndpoint
    form_class = forms.IVEndpointForm


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
