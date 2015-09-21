from __future__ import absolute_import

from assessment.api.views import AssessmentViewset
from utils.api import DisabledPagination

from . import models, serializers


class Study(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Study
    pagination_class = DisabledPagination

    def get_serializer_class(self):
        cls = serializers.VerboseStudySerializer
        if self.action == "list":
            cls = serializers.SimpleStudySerializer
        return cls

    def get_queryset(self):
        prefetch = ()
        if self.action != "list":
            prefetch = (
                'qualities',
                'identifiers',
                'qualities__metric',
                'qualities__metric__domain'
            )

        return self.model.objects.all()\
                   .select_related('assessment')\
                   .prefetch_related(*prefetch)
