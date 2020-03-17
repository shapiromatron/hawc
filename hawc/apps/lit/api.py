from rest_framework import decorators, mixins, viewsets
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions, AssessmentRootedTagTreeViewset
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet, LegacyAssessmentAdapterMixin
from ..common.renderers import PandasRenderers
from . import exports, models, serializers


class LiteratureAssessmentViewset(LegacyAssessmentAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
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

    @decorators.detail_route(
        methods=("get",), renderer_classes=PandasRenderers, url_path="reference-ids"
    )
    def reference_ids(self, request, pk):
        """
        Get literature reference ids for all assessment references
        """
        instance = self.get_object()
        qs = models.Reference.objects.assessment_qs(instance.id)
        df = models.Reference.objects.identifiers_dataframe(qs)
        return Response(df)

    @decorators.detail_route(
        methods=("get", "post"), url_path="reference-tags", renderer_classes=PandasRenderers
    )
    def reference_tags(self, request, pk):
        """
        Apply reference tags for all references in an assessment.
        """
        instance = self.get_object()

        if self.request.method == "POST":
            serializer = serializers.BulkReferenceTagSerializer(
                data=request.data, context={"assessment": instance}
            )
            serializer.is_valid(raise_exception=True)
            serializer.bulk_create_tags()

        df = models.ReferenceTags.objects.as_dataframe(instance.id)
        return Response(df)

    @decorators.detail_route(
        methods=("get", "post"), url_path="references-download", renderer_classes=PandasRenderers
    )
    def references_download(self, request, pk):
        """
        Get all references in an assessment.
        """

        self.set_legacy_attr(pk)

        self.tags = models.ReferenceFilterTag.get_all_tags(self.assessment.id, json_encode=False)

        exporter = exports.ReferenceFlatComplete(
            models.Reference.objects.get_qs(self.assessment).prefetch_related("identifiers"),
            export_format="excel",
            assessment=self.assessment,
            tags=self.tags,
        )

        return Response(exporter.build_dataframe())


class SearchViewset(viewsets.GenericViewSet, mixins.CreateModelMixin):
    model = models.Search
    serializer_class = serializers.SearchSerializer
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        return self.model.objects.all()


class ReferenceFilterTag(AssessmentRootedTagTreeViewset):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer


class ReferenceCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ReferenceCleanupFieldsSerializer
    model = models.Reference
    assessment_filter_args = "assessment"
