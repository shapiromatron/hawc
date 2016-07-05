from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class BMDSession(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.BMDSession
    serializer_class = serializers.BMDSessionSerializer
