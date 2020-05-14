from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response

from ..assessment.api import AssessmentViewset, DisabledPagination, InAssessmentFilter
from ..common.renderers import PandasRenderers
from ..common.helper import valid_values_or_404
from . import models, serializers


class UnpublishedFilter(BaseFilterBackend):
    """
    Only show unpublished visuals to admin and assessment members.
    """

    def filter_queryset(self, request, queryset, view):

        if not hasattr(view, "assessment"):
            try:
                int(view.kwargs["pk"])
            except ValueError:
                raise Http404(f"No 'pk' matches {view.kwargs['pk']}.")
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

    @action(detail=True, methods=("get",), renderer_classes=PandasRenderers)
    def data(self, request, pk):
        obj = self.get_object()
        export = obj.get_dataset()
        return Response(export)


class Visual(AssessmentViewset):
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

    def get_queryset(self):
        return super().get_queryset().select_related("assessment")
