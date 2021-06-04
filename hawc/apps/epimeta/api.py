from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions, AssessmentViewset
from ..assessment.models import Assessment
from ..common.api import LegacyAssessmentAdapterMixin
from ..common.helper import re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from . import actions, models, serializers


class EpiMetaAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.MetaResult
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @action(detail=True, methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Retrieve epidemiology metadata for assessment.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        exporter = actions.MetaResultFlatComplete(
            self.get_queryset(), filename=f"{self.assessment}-epi-meta"
        )
        return Response(exporter.build_export())


class MetaProtocol(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.MetaProtocol
    serializer_class = serializers.MetaProtocolSerializer


class MetaResult(AssessmentViewset):
    assessment_filter_args = "protocol__study__assessment"
    model = models.MetaResult
    serializer_class = serializers.MetaResultSerializer
