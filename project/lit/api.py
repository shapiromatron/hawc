from __future__ import absolute_import

from assessment.api.views import AssessmentRootedTagTreeViewset

from . import models, serializers


class ReferenceFilterTag(AssessmentRootedTagTreeViewset):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer
