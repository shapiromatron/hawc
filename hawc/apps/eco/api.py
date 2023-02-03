from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions
from ..assessment.models import Assessment
from ..common.api import LegacyAssessmentAdapterMixin
from ..common.helper import FlatExport, cacheable, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import models


class TermViewSet(viewsets.GenericViewSet):
    serializer_class = UnusedSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, renderer_classes=PandasRenderers)
    def nested(self, request: Request):
        def get_nested():
            df = models.NestedTerm.as_dataframe()
            return FlatExport(df=df, filename="eco-terms")

        export = cacheable(get_nested, "eco:api:terms-nested", "flush" in request.query_params)
        return Response(export)


class AssessmentViewset(LegacyAssessmentAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
    model = Assessment
    permission_classes = (AssessmentLevelPermissions,)
    filterset_class = None
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=True, renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Export entire ecological dataset.
        """
        instance = self.get_object()
        df = models.Result.complete_df(instance.id)
        export = FlatExport(df=df, filename=f"ecological-export-{self.assessment.id}")
        return Response(export)
