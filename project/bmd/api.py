from __future__ import absolute_import

from assessment.api import AssessmentViewset

from . import models, serializers


class BMD_session(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.BMD_session
    serializer_class = serializers.BMDSessionSerializer


class BMD_model_run(AssessmentViewset):
    assessment_filter_args = "BMD_session__endpoint__assessment"
    model = models.BMD_model_run
    serializer_class = serializers.BMDModelRunSerializer
