from __future__ import absolute_import

from rest_framework import viewsets
from rest_framework.response import Response

from api.permissions import AssessmentLevelPermissions, get_permitted_assessment

from . import models, serializers


class BMD_session(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AssessmentLevelPermissions, )
    model = models.BMD_session
    serializer_class = serializers.BMDSessionSerializer
    queryset = models.BMD_session.objects.all()

    def list(self, request):
        # override list to only return meta-results for a single assessment
        assessment = get_permitted_assessment(request)
        by_assessment = self.model.objects.filter(endpoint__assessment=assessment)
        page = self.paginate_queryset(by_assessment)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)


class BMD_model_run(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AssessmentLevelPermissions, )
    model = models.BMD_model_run
    serializer_class = serializers.BMDModelRunSerializer
    queryset = models.BMD_model_run.objects.all()

    def list(self, request):
        # override list to only return meta-results for a single assessment
        assessment = get_permitted_assessment(request)
        by_assessment = self.model.objects.filter(BMD_session__endpoint__assessment=assessment)
        page = self.paginate_queryset(by_assessment)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)
