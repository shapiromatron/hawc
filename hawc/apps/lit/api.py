import pandas as pd
import plotly.express as px
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentLevelPermissions, AssessmentRootedTagTreeViewset
from ..assessment.models import Assessment
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    OncePerMinuteThrottle,
)
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models, serializers


class LiteratureAssessmentViewset(LegacyAssessmentAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
    model = Assessment
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=True, methods=("get",), renderer_classes=PandasRenderers)
    def tags(self, request, pk):
        """
        Show literature tags for entire assessment.
        """
        instance = self.get_object()
        df = models.ReferenceFilterTag.as_dataframe(instance.id)
        export = FlatExport(df=df, filename=f"reference-tags-{self.assessment.id}")
        return Response(export)

    @action(
        detail=True, methods=("get",), renderer_classes=PandasRenderers, url_path="reference-ids"
    )
    def reference_ids(self, request, pk):
        """
        Get literature reference ids for all assessment references
        """
        instance = self.get_object()
        qs = models.Reference.objects.assessment_qs(instance.id)
        df = models.Reference.objects.identifiers_dataframe(qs)
        export = FlatExport(df=df, filename=f"reference-ids-{self.assessment.id}")
        return Response(export)

    @action(
        detail=True,
        methods=("get", "post"),
        url_path="reference-tags",
        renderer_classes=PandasRenderers,
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
        export = FlatExport(df=df, filename=f"reference-tags-{self.assessment.id}")
        return Response(export)

    @action(
        detail=True, methods=("get",), url_path="reference-year-histogram",
    )
    def reference_year_histogram(self, request, pk):
        instance = self.get_object()
        # get all the years for a given assessment
        years = list(
            models.Reference.objects.filter(assessment_id=instance.id, year__gt=0).values_list(
                "year", flat=True
            )
        )
        payload = {}
        if len(years) > 0:

            df = pd.DataFrame(years, columns=["Year"])
            nbins = min(max(df.Year.max() - df.Year.min() + 1, 4), 30)

            try:
                fig = px.histogram(df, x="Year", nbins=nbins)
            except ValueError:
                # in some cases a bad nbins can be provided; just use default bins instead
                # Invalid value of type 'numpy.int64' received for the 'nbinsx' property of histogram
                # [2005, 2013, 1995, 2001, 2017, 1991, 1991, 2009, 2006, 2005]; nbins=27
                fig = px.histogram(df, x="Year")

            fig.update_yaxes(title_text="# References")
            fig.update_xaxes(title_text="Year")
            fig.update_traces(marker=dict(color="#003d7b"))

            fig.update_layout(
                bargap=0.1,
                plot_bgcolor="white",
                autosize=True,
                margin=dict(l=0, r=0, t=30, b=0),  # noqa: E741
            )
            payload = fig.to_dict()

        return Response(payload)

    @action(
        detail=True, methods=("get",), url_path="topic-model",
    )
    def topic_model(self, request, pk):
        assessment = self.get_object()
        fig_dict = assessment.literature_settings.get_topic_tsne_fig_dict()
        return Response(fig_dict)

    @action(
        detail=True, methods=("post",), url_path="topic-model-request-refresh",
    )
    def topic_model_request_refresh(self, request, pk):
        assessment = self.get_object()
        if not assessment.user_can_edit_object(request.user):
            raise exceptions.PermissionDenied()
        assessment.literature_settings.topic_tsne_refresh_requested = timezone.now()
        assessment.literature_settings.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("get",),
        url_path="references-download",
        renderer_classes=PandasRenderers,
    )
    def references_download(self, request, pk):
        """
        Get all references in an assessment.
        """
        assessment = self.get_object()
        tags = models.ReferenceFilterTag.get_all_tags(assessment.id, json_encode=False)
        exporter = exports.ReferenceFlatComplete(
            models.Reference.objects.get_qs(assessment)
            .prefetch_related("identifiers")
            .order_by("id"),
            filename=f"references-{assessment}",
            assessment=assessment,
            tags=tags,
        )
        return Response(exporter.build_export())

    @action(detail=True, renderer_classes=PandasRenderers, url_path="tag-heatmap")
    def tag_heatmap(self, request, pk):
        """
        Get tags formatted in a long format desireable for heatmaps.
        """
        instance = self.get_object()
        key = f"assessment-{instance.id}-lit-tag-heatmap"
        df = cache.get(key)
        if df is None:
            df = models.Reference.objects.heatmap_dataframe(instance.id)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"df-{instance.id}")
        return Response(export)

    @transaction.atomic()
    @action(
        detail=True,
        throttle_classes=(OncePerMinuteThrottle,),
        methods=("post",),
        url_path="replace-hero",
    )
    def replace_hero(self, request, pk):
        """Replace old HERO ID with new HERO ID for selected references

        Expects an input of `{replace: [[1,10],[2,20],[3,30]]}`, a list of lists with two items in each
        inner list. Each inner list contains the reference ID and the new HERO ID, respectively.
        """
        assessment = self.get_object()
        serializer = serializers.ReferenceReplaceHeroIdSerializer(
            data=request.data, context={"assessment": assessment}
        )
        serializer.is_valid(raise_exception=True)
        serializer.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic()
    @action(
        detail=True,
        throttle_classes=(OncePerMinuteThrottle,),
        methods=("post",),
        url_path="update-reference-metadata-from-hero",
    )
    def update_reference_metadata_from_hero(self, request, pk):
        """
        Query HERO for all references in an assessment that are mapped to HERO, fetch the latest
        metadata from HERO, and then update the reference metadata in HAWC with the data from HERO.
        """
        assessment = self.get_object()
        models.Reference.update_hero_metadata(assessment.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=("post",), url_path="reference-search")
    def reference_search(self, request, pk):
        assessment = self.get_object()
        if not assessment.user_can_view_object(request.user):
            raise exceptions.PermissionDenied()

        serializer = serializers.ReferenceQuerySerializer(
            data=request.data, context={"assessment": assessment}
        )

        resp = []
        if serializer.is_valid(raise_exception=True):
            resp = serializer.search()

        return Response(dict(references=resp))


class SearchViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = models.Search
    serializer_class = serializers.SearchSerializer
    permission_classes = (AssessmentLevelPermissions,)
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @action(
        detail=True, methods=("get",), renderer_classes=PandasRenderers,
    )
    def references(self, request, pk):
        """
        Return all references for a given Search
        """
        instance = self.get_object()
        exporter = exports.ReferenceFlatComplete(
            instance.references.all(),
            filename=f"{instance.assessment}-search-{instance.slug}",
            assessment=self.assessment,
            tags=models.ReferenceFilterTag.get_all_tags(self.assessment.id, json_encode=False),
            include_parent_tag=False,
        )
        return Response(exporter.build_export())


class ReferenceFilterTagViewset(AssessmentRootedTagTreeViewset):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer

    @action(detail=True, renderer_classes=PandasRenderers)
    def references(self, request, pk):
        """
        Return all references for a selected tag; does not include tag-descendants.
        """
        tag = self.get_object()
        exporter = exports.ReferenceFlatComplete(
            queryset=models.Reference.objects.filter(tags=tag).order_by("id"),
            filename=f"{self.assessment}-{tag.slug}",
            assessment=self.assessment,
            tags=self.model.get_all_tags(self.assessment.id, json_encode=False),
            include_parent_tag=False,
        )
        return Response(exporter.build_export())

    @action(detail=True, url_path="references-table-builder", renderer_classes=PandasRenderers)
    def references_table_builder(self, request, pk):
        """
        Return all references for a selected tag in table-builder import format; does not include
        tag-descendants.
        """
        tag = self.get_object()
        exporter = exports.TableBuilderFormat(
            queryset=models.Reference.objects.filter(tags=tag).order_by("id"),
            filename=f"{self.assessment}-{tag.slug}",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())


class ReferenceCleanupViewset(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ReferenceCleanupFieldsSerializer
    model = models.Reference
    assessment_filter_args = "assessment"


class ReferenceViewset(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.ReferenceSerializer
    permission_classes = (AssessmentLevelPermissions,)
    queryset = models.Reference.objects.all()
