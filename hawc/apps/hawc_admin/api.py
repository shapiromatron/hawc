from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..assessment.exports import ValuesListExport
from ..assessment.models import AssessmentValue
from ..common.api import FivePerMinuteThrottle
from ..common.helper import FlatExport
from ..common.renderers import PandasRenderers
from .actions import media_metadata_report


class DashboardViewset(viewsets.ViewSet):

    permission_classes = (permissions.IsAdminUser,)
    renderer_classes = (JSONRenderer,)

    @action(detail=False, renderer_classes=PandasRenderers)
    def media(self, request):
        uri = request.build_absolute_uri(location="/")[:-1]
        df = media_metadata_report(uri)
        export = FlatExport(df=df, filename=f"media-{timezone.now().strftime('%Y-%m-%d')}")
        return Response(export)


class DiagnosticViewset(viewsets.ViewSet):
    permission_classes = (permissions.IsAdminUser,)

    @action(detail=False, throttle_classes=(FivePerMinuteThrottle,))
    def throttle(self, request):
        throttle = self.get_throttles()[0]
        return Response({"identity": throttle.get_ident(request)})


class ReportsViewset(viewsets.ViewSet):
    permission_classes = (permissions.IsAdminUser,)

    @action(detail=False, renderer_classes=PandasRenderers)
    def values(self, request):
        """Gets all value data accross all assessments."""
        export = ValuesListExport(
            queryset=AssessmentValue.objects.all(), filename="hawc-assessment-values"
        ).build_export()
        return Response(export, status=status.HTTP_200_OK)
