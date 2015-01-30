from __future__ import absolute_import

from api.permissions import AssessmentViewset

from . import models, serializers


class Endpoint(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
