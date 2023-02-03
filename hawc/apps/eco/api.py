from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..common.helper import FlatExport, cacheable
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
