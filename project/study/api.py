from __future__ import absolute_import

from api.permissions import AssessmentViewset

from . import models, serializers


class Study(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Study
    serializer_class = serializers.VerboseStudySerializer
