from __future__ import absolute_import

from rest_framework.decorators import detail_route
from rest_framework.response import Response

from assessment.api.views import AssessmentViewset, AssessmentEditViewset, \
    AssessmentLevelPermissions

from . import models, serializers, tasks


class BMDSession(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.BMDSession

    def get_serializer_class(self):
        if self.action == 'execute':
            return serializers.BMDSessionUpdateSerializer
        else:
            return serializers.BMDSessionSerializer

    @detail_route(methods=['post'])
    def execute(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tasks.execute.delay(instance.id)
        return Response({'started': True})

    @detail_route(methods=['get'])
    def execute_status(self, request, pk=None):
        # ping until execution is complete
        session = self.get_object()
        return Response({'finished': session.is_finished})

    @detail_route(methods=['post'])
    def selected_model(self, request, pk=None):
        # get_or_create selected model for this endpoint; use serializer
        session = self.get_object()
        return Response({'status': 'selected_model'})
