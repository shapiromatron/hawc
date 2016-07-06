from __future__ import absolute_import

from rest_framework.decorators import detail_route
from rest_framework.response import Response

from assessment.api.views import AssessmentViewset, AssessmentEditViewset, \
    AssessmentLevelPermissions

from . import models, serializers


class BMDSession(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.BMDSession
    serializer_class = serializers.BMDSessionSerializer

    @detail_route(methods=['post'])
    def execute(self, request, pk=None):
        session = self.get_object()
        # 1. get bmrs and models in serializer
        # 2. save
        # 3. kick off execution task
        return Response({'status': 'bmd executed'})

    @detail_route(methods=['get'])
    def execute_status(self, request, pk=None):
        # ping until execution is complete
        session = self.get_object()
        return Response({'status': session.get_execute_status()})

    @detail_route(methods=['post'])
    def selected_model(self, request, pk=None):
        # get_or_create selected model for this endpoint; use serializer
        session = self.get_object()
        return Response({'status': 'selected_model'})
