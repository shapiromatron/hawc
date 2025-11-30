from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..diagnostics import worker_healthcheck


class HealthcheckViewSet(viewsets.ViewSet):
    @action(detail=False)
    def web(self, request):
        return Response({"healthy": True})

    @action(detail=False)
    def worker(self, request):
        is_healthy = worker_healthcheck.healthy()
        # don't use 5xx email; django logging catches and sends error emails
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_400_BAD_REQUEST
        return Response({"healthy": is_healthy}, status=status_code)
