from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..assessment.api import AssessmentLevelPermissions
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.helper import FlatExport, cacheable, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models


class TermViewSet(GenericViewSet):
    serializer_class = UnusedSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, renderer_classes=PandasRenderers)
    def nested(self, request: Request):
        def get_nested():
            df = models.NestedTerm.as_dataframe()
            return FlatExport(df=df, filename="eco-terms")

        export = cacheable(get_nested, "eco:api:terms-nested", "flush" in request.query_params)
        return Response(export)


class AssessmentViewSet(GenericViewSet):
    model = Assessment
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @action(
        detail=True,
        renderer_classes=PandasRenderers,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
    )
    def export(self, request, pk):
        """
        Export entire ecological dataset.
        """
        instance = self.get_object()
        df = models.Result.complete_df(instance.id)
        export = FlatExport(df=df, filename=f"ecological-export-{self.assessment.id}")
        return Response(export)

    @action(
        detail=True,
        url_path="study-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def study_export(self, request, pk):
        """
        Retrieve epidemiology at the study level for assessment.
        """
        assessment: Assessment = self.get_object()
        published_only = not assessment.user_can_edit_object(request.user)
        qs = models.Result.objects.get_qs(assessment).published_only(published_only).complete()
        exporter = exports.EcoStudyComplete(qs, filename=f"{assessment}-eco-study")
        return Response(exporter.build_export())
