from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class Study(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Study
    serializer_class = serializers.VerboseStudySerializer

    def get_queryset(self):
        return self.model.objects.all()\
                .select_related(
                    'assessment'
                ).prefetch_related(
                    'qualities',
                    'identifiers',
                    'qualities__metric',
                    'qualities__metric__domain'
                )
