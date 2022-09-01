from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from hawc.apps.assessment.models import Assessment
from hawc.apps.common.api.mixins import LegacyAssessmentAdapterMixin
from hawc.apps.common.renderers import PandasRenderers
from hawc.apps.common.serializers import UnusedSerializer
from hawc.apps.common.views import AssessmentPermissionsMixin

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions
from ..common.api.viewsets import EditPermissionsCheckMixin
from . import exports, models, serializers


class Design(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Design
    serializer_class = serializers.DesignSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()


class EpiAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.DataExtraction
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment).complete()
        return self.model.objects.get_qs(self.assessment).complete()

    @action(detail=True, url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Retrieve epidemiology data for assessment.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        exporter = exports.EpiFlatComplete(self.get_queryset(), filename=f"{self.assessment}-epi")
        return Response(exporter.build_export())
