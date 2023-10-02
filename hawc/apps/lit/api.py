from zipfile import BadZipFile

import pandas as pd
import plotly.express as px
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied, ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from ..assessment.api import (
    METHODS_NO_PUT,
    AssessmentLevelPermissions,
    AssessmentRootedTagTreeViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api import OncePerMinuteThrottle, PaginationWithCount
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.views import create_object_log
from . import constants, exports, filterset, models, serializers


class LiteratureAssessmentViewSet(viewsets.GenericViewSet):
    model = Assessment
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    filterset_class = None
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def tags(self, request, pk):
        """
        Show literature tags for entire assessment.
        """
        instance = self.get_object()
        df = models.ReferenceFilterTag.as_dataframe(instance.id)
        return FlatExport.api_response(df=df, filename=f"reference-tags-{self.assessment.id}")

    @action(detail=True, methods=("get", "post"), permission_classes=(permissions.AllowAny,))
    def tagtree(self, request, pk, *args, **kwargs):
        """
        Get/Update literature tags for an assessment in tree-based structure
        """
        assessment = self.get_object()
        context = context = {"assessment": assessment}
        if self.request.method == "GET":
            if not assessment.user_can_view_object(request.user):
                raise exceptions.PermissionDenied()
            serializer = serializers.ReferenceTreeSerializer(instance={}, context=context)
        elif self.request.method == "POST":
            if not assessment.user_can_edit_object(request.user):
                raise exceptions.PermissionDenied()
            serializer = serializers.ReferenceTreeSerializer(data=request.data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.update()
            create_object_log(
                "Updated (tagtree replace)", assessment, assessment.id, self.request.user.id
            )
        else:
            raise ValueError()
        return Response(serializer.data)

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        pagination_class=PaginationWithCount,
    )
    def references(self, request, pk):
        """
        Get references for an assessment

        Args (via GET parameters):
            - search_id: gets references within a given search
            - tag_id: gets references with a given tagTag object id; if provided, gets references with tag
            - all: fetch all references without pagination (default False)
            - untagged: include untagged references (default False)
            - required_tags: requires references to have at least one of the given tags
            - pruned_tags: prunes references with any of the given tags if they no longer belong in the subtree without said tag
        """
        assessment = self.get_object()
        ref_filters = serializers.FilterReferences.from_drf(
            request.query_params, assessment_id=assessment.pk
        )
        qs = ref_filters.get_queryset()

        if "all" in request.query_params:
            serializer = serializers.ReferenceSerializer(qs, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qs)
            serializer = serializers.ReferenceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
        url_path="reference-ids",
    )
    def reference_ids(self, request, pk):
        """
        Get literature reference ids for all assessment references
        """
        instance = self.get_object()
        qs = instance.references.all()
        df = models.Reference.objects.identifiers_dataframe(qs)
        return FlatExport.api_response(df=df, filename=f"reference-ids-{self.assessment.id}")

    @action(
        detail=True,
        methods=("get", "post"),
        url_path="reference-tags",
        permission_classes=(permissions.AllowAny,),
        renderer_classes=PandasRenderers,
    )
    def reference_tags(self, request, pk):
        """
        Apply reference tags for all references in an assessment.
        """
        assessment = self.get_object()

        if self.request.method == "GET":
            if not assessment.user_can_view_object(request.user):
                raise exceptions.PermissionDenied()
        if self.request.method == "POST":
            if not assessment.user_can_edit_object(request.user):
                raise exceptions.PermissionDenied()
            serializer = serializers.BulkReferenceTagSerializer(
                data=request.data, context={"assessment": assessment}
            )
            serializer.is_valid(raise_exception=True)
            serializer.bulk_create_tags()

        df = models.ReferenceTags.objects.as_dataframe(assessment.id)
        return FlatExport.api_response(df=df, filename=f"reference-tags-{assessment.id}")

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        url_path="reference-year-histogram",
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
                margin=dict(l=0, r=0, t=30, b=0),
            )
            payload = fig.to_dict()

        return Response(payload)

    @action(
        detail=True,
        url_path="reference-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def reference_export(self, request, pk):
        """
        Get all references in an assessment.
        """
        assessment = self.get_object()
        queryset = (
            models.Reference.objects.get_qs(assessment)
            .prefetch_related("identifiers", "tags")
            .order_by("id")
        )
        fs = filterset.ReferenceExportFilterSet(
            data=request.query_params,
            queryset=queryset,
            request=request,
        )
        if not fs.is_valid():
            raise ValidationError(fs.errors)

        tags = models.ReferenceFilterTag.get_all_tags(assessment.id)
        Exporter = (
            exports.TableBuilderFormat
            if request.query_params.get("export_format") == "table-builder"
            else exports.ReferenceFlatComplete
        )
        export = Exporter(
            queryset=fs.qs,
            filename=f"references-{assessment.name}",
            assessment=assessment,
            tags=tags,
        )
        return Response(export.build_export())

    @action(
        detail=True,
        url_path="user-tag-export",
        renderer_classes=PandasRenderers,
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
    )
    def user_tag_export(self, request, pk):
        """
        Get all references in an assessment, including all user tag data.
        """
        assessment = self.get_object()
        tags = models.ReferenceFilterTag.get_all_tags(assessment.id)
        qs = (
            models.UserReferenceTag.objects.filter(reference__assessment=assessment.id)
            .select_related("reference", "user")
            .prefetch_related("tags", "reference__identifiers")
            .order_by("reference_id", "id")
        )
        exporter = exports.ReferenceFlatComplete(
            qs,
            filename=f"references-user-tags-{assessment.name}",
            assessment=assessment,
            tags=tags,
            user_tags=True,
        )
        return Response(exporter.build_export())

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
        url_path="tag-heatmap",
    )
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
        return FlatExport.api_response(df=df, filename=f"df-{instance.id}")

    @transaction.atomic
    @action(
        detail=True,
        throttle_classes=(OncePerMinuteThrottle,),
        methods=("post",),
        url_path="replace-hero",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
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
        create_object_log(
            "Updated (HERO replacements)", assessment, assessment.id, self.request.user.id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    @action(
        detail=True,
        throttle_classes=(OncePerMinuteThrottle,),
        methods=("post",),
        url_path="update-reference-metadata-from-hero",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
    )
    def update_reference_metadata_from_hero(self, request, pk):
        """
        Query HERO for all references in an assessment that are mapped to HERO, fetch the latest
        metadata from HERO, and then update the reference metadata in HAWC with the data from HERO.
        """
        assessment = self.get_object()
        models.Reference.update_hero_metadata(assessment.id)
        create_object_log(
            "Updated (HERO metadata)", assessment, assessment.id, self.request.user.id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("post",),
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        parser_classes=(FileUploadParser,),
        renderer_classes=PandasRenderers,
        url_path="excel-to-json",
    )
    def excel_to_json(self, request, pk):
        self.get_object()  # permissions check

        file_ = request.data.get("file")

        if file_ is None:
            raise ValidationError({"file": "A file is required"})
        elif not file_.name.endswith(".xlsx"):
            raise ValidationError({"file": "File extension must be .xlsx"})

        try:
            # engine required since this is a BytesIO stream
            df = pd.read_excel(file_, engine="openpyxl")
        except (BadZipFile, ValueError):
            raise ParseError({"file": "Unable to parse excel file"})

        return FlatExport.api_response(df=df, filename=file_.name)


class SearchViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = models.Search
    serializer_class = serializers.SearchSerializer
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all()


class ReferenceFilterTagViewSet(AssessmentRootedTagTreeViewSet):
    model = models.ReferenceFilterTag
    serializer_class = serializers.ReferenceFilterTagSerializer


class ReferenceViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = METHODS_NO_PUT
    serializer_class = serializers.ReferenceSerializer
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    queryset = models.Reference.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("tag", "resolve_conflict"):
            qs = qs.select_related("assessment__literature_settings").prefetch_related(
                "user_tags__tags", "tags"
            )
        return qs

    @action(
        detail=True, methods=("post",), action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT
    )
    def tag(self, request, pk):
        response = {"status": "fail"}
        instance = self.get_object()
        assessment = instance.assessment
        if assessment.user_can_edit_object(self.request.user):
            try:
                tags = [int(tag) for tag in self.request.data.get("tags", [])]
                resolved = instance.update_tags(request.user, tags)
            except ValueError:
                return Response({"tags": "Array of tags must be valid primary keys"}, status=400)
            response["status"] = "success"
            response["resolved"] = resolved
        return Response(response)

    @action(
        detail=True, methods=("post",), action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT
    )
    def merge_tags(self, request, pk):
        response = {"status": "fail"}
        instance = self.get_object()
        assessment = instance.assessment
        if not assessment.user_can_edit_object(self.request.user):
            raise PermissionDenied()
        try:
            instance.merge_tags(self.request.user)
        except ValueError:
            return Response({"reference": "Reference has no user tags to merge."}, status=400)
        response["status"] = "success"
        return Response(response)

    @action(
        detail=True, methods=("post",), action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT
    )
    def resolve_conflict(self, request, pk):
        instance = self.get_object()
        assessment = instance.assessment
        if not assessment.user_can_edit_object(self.request.user):
            raise PermissionDenied()
        user_reference_tag = get_object_or_404(
            models.UserReferenceTag,
            reference_id=instance.id,
            id=int(request.POST.get("user_tag_id", -1)),
        )
        instance.resolve_user_tag_conflicts(self.request.user.id, user_reference_tag)
        return Response({"status": "ok"})

    @action(
        detail=False,
        url_path=r"search/type/(?P<db_id>[\d])/id/(?P<id>.*)",
        renderer_classes=PandasRenderers,
        permission_classes=(permissions.IsAdminUser,),
    )
    def id_search(self, request, id: str, db_id: int):
        db_id = int(db_id)
        if db_id not in constants.ReferenceDatabase:
            raise ValidationError({"type": f"Must be in {constants.ReferenceDatabase.choices}"})
        qs = self.get_queryset().filter(identifiers__unique_id=id, identifiers__database=db_id)
        return FlatExport.api_response(
            df=qs.global_df(),
            filename=f"global-reference-data-{id}",
        )
