from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from ..assessment.api import (
    AssessmentEditViewSet,
    AssessmentViewSet,
    BaseAssessmentViewSet,
    EditPermissionsCheckMixin,
    InAssessmentFilter,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api import DisabledPagination
from ..common.helper import FlatExport
from ..common.renderers import DocxRenderer, PandasRenderers
from ..common.serializers import UnusedSerializer
from . import models, serializers, table_serializers


class UnpublishedFilter(BaseFilterBackend):
    """
    Only show unpublished visuals to admin and assessment members.
    """

    def filter_queryset(self, request, queryset, view):
        if not hasattr(view, "assessment"):
            self.instance = get_object_or_404(queryset.model, **view.kwargs)
            view.assessment = self.instance.get_assessment()

        if not view.assessment.user_is_reviewer_or_higher(request.user):
            queryset = queryset.filter(published=True)
        return queryset


class SummaryAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="visual-heatmap-datasets",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
    )
    def heatmap_datasets(self, request, pk):
        """Returns a list of the heatmap datasets available for an assessment."""
        instance = self.get_object()
        datasets = models.Visual.get_heatmap_datasets(instance).model_dump()
        return Response(datasets)


class DataPivotViewSet(AssessmentViewSet):
    """
    For list view, return simplified data-pivot view.

    For all other views, use the detailed visual view.
    """

    assessment_filter_args = "assessment"
    model = models.DataPivot
    pagination_class = DisabledPagination
    filter_backends = (InAssessmentFilter, UnpublishedFilter)

    def get_queryset(self):
        return self.model.objects.select_related("datapivotquery", "datapivotupload").all()

    def get_serializer_class(self):
        cls = serializers.DataPivotSerializer
        if self.action == "list":
            cls = serializers.CollectionDataPivotSerializer
        return cls

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def data(self, request, pk):
        obj = self.get_object()
        export = obj.get_dataset()
        return Response(export)


class DataPivotQueryViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.DataPivotQuery
    filter_backends = (InAssessmentFilter, UnpublishedFilter)
    serializer_class = serializers.DataPivotQuerySerializer


class VisualViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    """
    For list view, return all Visual objects for an assessment, but using the
    simplified collection view.

    For all other views, use the detailed visual view.
    """

    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.Visual
    pagination_class = DisabledPagination
    filter_backends = (InAssessmentFilter, UnpublishedFilter)

    def get_serializer_class(self):
        cls = serializers.VisualSerializer
        if self.action == "list":
            cls = serializers.CollectionVisualSerializer
        return cls

    def get_queryset(self):
        return super().get_queryset().select_related("assessment")

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def data(self, request, pk):
        obj = self.get_object()
        try:
            df = obj.data_df()
        except ValueError:
            return Response(
                {"error": "Data export not available for this visual type."},
                status=HTTP_400_BAD_REQUEST,
            )
        return FlatExport.api_response(df, obj.slug)


class SummaryTextViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.SummaryText
    pagination_class = DisabledPagination
    filter_backends = (InAssessmentFilter,)
    serializer_class = serializers.SummaryTextSerializer

    def get_queryset(self):
        return self.model.objects.all()


class SummaryTableViewSet(AssessmentEditViewSet):
    assessment_filter_args = "assessment"
    model = models.SummaryTable
    filter_backends = (InAssessmentFilter, UnpublishedFilter)
    serializer_class = serializers.SummaryTableSerializer
    list_actions = ["list", "data"]

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=(DocxRenderer,),
    )
    def docx(self, request, pk):
        obj = self.get_object()
        report = obj.to_docx(base_url=request._current_scheme_host)
        return Response(report)

    @action(detail=False, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def data(self, request):
        ser = table_serializers.SummaryTableDataSerializer(
            data=request.query_params.dict(), context=self.get_serializer_context()
        )
        ser.is_valid(raise_exception=True)
        # get cached value
        cache_key = f"assessment-{self.assessment.id}-summary-table-{ser.cache_key}"
        data = cache.get(cache_key)
        if data is None:
            # if cached value does not exist, get the data and set the cache
            data = ser.get_data()
            cache.set(cache_key, data, settings.CACHE_1_HR)
        return Response(data)
