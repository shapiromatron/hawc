from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..assessment.api import (
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api.utils import get_published_only
from ..common.helper import FlatExport, cacheable
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..study.models import Study
from . import models, serializers


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


class AssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        renderer_classes=PandasRenderers,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
    )
    def export(self, request, pk):
        """
        Export entire ecological dataset.
        """
        assessment = self.get_object()
        published_only = get_published_only(assessment, request)
        qs = models.Result.objects.assessment_qs(assessment.id).published_only(published_only)
        return FlatExport.api_response(
            df=qs.complete_df(), filename=f"ecological-export-{assessment.id}"
        )

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
        published_only = get_published_only(assessment, request)
        qs = (
            Study.objects.assessment_qs(assessment.id)
            .filter(eco=True)
            .published_only(published_only)
        )
        df = models.Design.objects.study_df(qs)
        return FlatExport.api_response(df=df, filename=f"ecological-study-export-{assessment.id}")


class DesignCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.DesignCleanupSerializer
    model = models.Design
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")


class CauseCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.CauseCleanupSerializer
    model = models.Cause
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")


class EffectCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.EffectCleanupSerializer
    model = models.Effect
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")


class ResultCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ResultCleanupSerializer
    model = models.Result
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")
