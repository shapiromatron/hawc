from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    BaseAssessmentViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models


class UdfAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="model-export",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export_model(self, request, pk):
        """
        UDF complete export.

        Must be able to edit objects because this could show data about content which is not
        from a published study.
        """
        assessment: Assessment = self.get_object()
        export_name = f"{assessment}-udf-model"
        qs = models.ModelUDFContent.objects.assessment_qs(assessment)
        content_type = request.query_params.get("content_type", "").split(".")
        if len(content_type) == 2:
            qs = qs.filter_content_type(app=content_type[0], model=content_type[1])
        exporter = exports.ModelUDFContentExporter.flat_export(qs, filename=export_name)
        return Response(exporter)
