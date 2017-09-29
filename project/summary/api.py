from rest_framework.filters import BaseFilterBackend
from assessment.api import AssessmentViewset, DisabledPagination, InAssessmentFilter

from . import models, serializers


class UnpublishedFilter(BaseFilterBackend):
    """
        Only show unpublished visuals to admin and assessment members.
    """
    def get_unpublished_perms(self, user, view):
        return ((user.is_superuser) or
                (user in view.assessment.project_manager.all()) or
                (user in view.assessment.team_members.all()) or
                (user in view.assessment.reviewers.all()))

    def filter_queryset(self, request, queryset, view):
        if not self.get_unpublished_perms(request.user, view):
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
