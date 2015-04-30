from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class DataPivot(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.DataPivot
    serializer_class = serializers.DataPivotSerializer
    paginate_by = None


class Visual(AssessmentViewset):
    """
    For list view, return all Visual objects for an assessment, but using the
    simplified collection view.

    For all other views, use the detailed visual view.
    """

    assessment_filter_args = "assessment"
    model = models.Visual
    paginate_by = None

    def get_serializer_class(self):
        cls = serializers.VisualSerializer
        if self.action == "list":
            cls  = serializers.CollectionVisualSerializer
        return cls
