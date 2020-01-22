from rest_framework import decorators, viewsets
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions, AssessmentRootedTagTreeViewset
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet
from ..common.renderers import PandasRenderers
from . import models, serializers


class LiteratureAssessmentViewset(viewsets.GenericViewSet):
    model = Assessment
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        return self.model.objects.all()

    @decorators.detail_route(methods=("get",), renderer_classes=PandasRenderers)
    def tags(self, request, pk):
        """
        Show literature tags for entire assessment.
        """
        instance = self.get_object()
        df = models.ReferenceFilterTag.as_dataframe(instance.id)
        return Response(df)


class ReferenceFilterTag(AssessmentRootedTagTreeViewset):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer


class ReferenceCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ReferenceCleanupFieldsSerializer
    model = models.Reference
    assessment_filter_args = "assessment"
