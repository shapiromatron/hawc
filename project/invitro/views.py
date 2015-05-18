from assessment.models import Assessment
from utils.views import GenerateReport, BaseList, BaseDetail

from . import models, exports


class ExperimentDetail(BaseDetail):
    model = models.IVExperiment


class EndpointDetail(BaseDetail):
    model = models.IVEndpoint


class EndpointsFullExport(BaseList):
    parent_model = Assessment
    model = models.IVEndpoint

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsFullExport, self).get_obj_perms()
        if not perms['edit']:
            filters["experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        export_format = request.GET.get("output", "excel")
        exporter = exports.IVEndpointFlatDataPivot(
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
