from __future__ import absolute_import

from assessment.api import AssessmentViewset

from . import models, serializers


class MetaProtocol(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.MetaProtocol
    serializer_class = serializers.MetaProtocolSerializer


class MetaResult(AssessmentViewset):
    assessment_filter_args = "protocol__study__assessment"
    model = models.MetaResult
    serializer_class = serializers.MetaResultSerializer
