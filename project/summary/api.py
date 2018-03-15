from django.shortcuts import get_object_or_404
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from assessment.api import AssessmentViewset, AssessmentEditViewset, DisabledPagination, InAssessmentFilter

from . import models, serializers


class UnpublishedFilter(BaseFilterBackend):
    """
    Only show unpublished visuals to admin and assessment members.
    """

    def filter_queryset(self, request, queryset, view):

        if not hasattr(view, 'assessment'):
            self.instance = get_object_or_404(queryset.model, **view.kwargs)
            view.assessment = self.instance.get_assessment()

        if not view.assessment.user_is_part_of_team(request.user):
            queryset = queryset.filter(published=True)
        return queryset


class DataPivot(AssessmentViewset):
    """
    For list view, return simplified data-pivot view.

    For all other views, use the detailed visual view.
    """
    assessment_filter_args = "assessment"
    model = models.DataPivot
    pagination_class = DisabledPagination
    filter_backends = (InAssessmentFilter, UnpublishedFilter)

    def get_serializer_class(self):
        cls = serializers.DataPivotSerializer
        if self.action == "list":
            cls = serializers.CollectionDataPivotSerializer
        return cls


class Visual(AssessmentEditViewset):
    """
    For list view, return all Visual objects for an assessment, but using the
    simplified collection view.

    For all other views, use the detailed visual view.
    """

    assessment_filter_args = "assessment"
    model = models.Visual
    pagination_class = DisabledPagination
    filter_backends = (InAssessmentFilter, UnpublishedFilter)

    def get_serializer_class(self):
        cls = serializers.VisualSerializer
        if self.action == "list":
            cls = serializers.CollectionVisualSerializer
        return cls

    def update(self, request, *args, **kwargs):
        assessment = kwargs.pop('assessment', None)
        visual_type = kwargs.pop('visual_type', None)
        instance = self.get_object()
        if assessment:
            instance.assessment = assessment
        if visual_type is not None:  # required if value is 0
            instance.visual_type = visual_type

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
