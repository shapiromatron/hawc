from django.http import HttpResponse

from assessment.models import Assessment
from utils.views import BaseDetail, BaseList

from . import models


# class ExperimentDetail(BaseDetail):
#     model = models.Experiment


# class EndpointDetail(BaseDetail):
#     model = models.IVEndpoint


class EndpointsFlat(BaseList):
    parent_model = Assessment
    model = models.IVEndpoint

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsFlat, self).get_obj_perms()
        if not perms['edit']:
            filters["experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        output_type = request.GET.get('output', None)
        if output_type == 'tsv':
            tsv = self.model.get_tsv_file(self.object_list)
            response = HttpResponse(tsv, content_type='text/tab-separated-values')
            response['Content-Disposition'] = 'attachment; filename="download.tsv"'
        else:
            xls = self.model.get_excel_file(self.object_list)
            response = HttpResponse(xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="download.xls"'

        return response

