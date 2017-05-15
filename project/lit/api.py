

from assessment.api import AssessmentRootedTagTreeViewset

from . import models, serializers


class ReferenceFilterTag(AssessmentRootedTagTreeViewset):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer
