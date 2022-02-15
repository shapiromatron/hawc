from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..common.diagnostics import worker_healthcheck
from ..common.helper import FlatExport
from ..common.renderers import PandasRenderers, SvgRenderer
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


class HealthcheckViewset(viewsets.ViewSet):
    @action(detail=False)
    def web(self, request):
        return Response({"healthy": True})

    @action(detail=False)
    def worker(self, request):
        is_healthy = worker_healthcheck.healthy()
        # don't use 5xx email; django logging catches and sends error emails
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_400_BAD_REQUEST
        return Response({"healthy": is_healthy}, status=status_code)

    @action(
        detail=False,
        url_path="worker-plot",
        renderer_classes=(SvgRenderer,),
        permission_classes=(permissions.IsAdminUser,),
    )
    def worker_plot(self, request):
        ax = worker_healthcheck.plot()
        return Response(ax)

    @action(detail=False, url_path="worker-stats", permission_classes=(permissions.IsAdminUser,))
    def worker_stats(self, request):
        return Response(worker_healthcheck.stats())
