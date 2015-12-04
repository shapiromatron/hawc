from __future__ import absolute_import

from django.shortcuts import get_object_or_404

from rest_framework.decorators import list_route
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets

from assessment.api import views as assessment_views
from assessment import models as assessment_models
from . import views

class DisabledPagination(PageNumberPagination):
    page_size = None

class CleanupFieldsBaseViewSet(views.ProjectManagerOrHigherMixin, viewsets.ModelViewSet):
    parent_model = assessment_models.Assessment
    assessment_filter_args = "assessment"
    permission_classes = (assessment_views.AssessmentLevelPermissions, )
    filter_backends = (assessment_views.InAssessmentFilter, )
    template_name = 'assessment/endpointcleanup_list.html'

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(self.parent_model, pk=request.GET.get('assessment_id'))

    def get_queryset(self):
        return self.model.objects.all()

    @list_route(methods=['get'])
    def fields(self, request, format=None):
        cleanup_fields = self.model.text_cleanup_fields()
        return Response({'text_cleanup_fields': cleanup_fields})
