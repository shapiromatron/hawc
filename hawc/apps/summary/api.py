from uuid import uuid4

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from ..assessment.api import (
    AssessmentEditViewSet,
    BaseAssessmentViewSet,
    EditPermissionsCheckMixin,
    InAssessmentFilter,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api import DisabledPagination
from ..common.api.validation import get_enum_or_400
from ..common.helper import FlatExport, PydanticToDjangoError, cacheable, tryParseInt
from ..common.renderers import DocxRenderer, PandasRenderers
from ..common.serializers import UnusedSerializer
from . import constants, forms, models, schemas, serializers, table_serializers


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

    @action(
        detail=True,
        methods=("post",),
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
    )
    def json_data(self, request, pk):
        """Get json data for a Visual; designed for create/update operations."""
        assessment = self.get_object()

        # get visual_type
        visual_type = get_enum_or_400(
            tryParseInt(request.data.get("visual_type", -1)), constants.VisualType
        )

        if visual_type == constants.VisualType.BIOASSAY_CROSSVIEW:
            data = request.data.copy()
            uuid = "zzz-zzz" if settings.IS_TESTING else str(uuid4())
            evidence_type = constants.StudyType.BIOASSAY
            data.update(title=uuid, slug=uuid, evidence_type=evidence_type)
            form = forms.CrossviewForm(
                data, evidence_type=evidence_type, visual_type=visual_type, parent=assessment
            )
            if form.is_valid() is False:
                raise ValidationError(form.errors)
            instance = form.save(commit=False)
            return Response(serializers.VisualSerializer(instance).data)

        # check ROB style visuals
        if visual_type in [constants.VisualType.ROB_HEATMAP, constants.VisualType.ROB_BARCHART]:
            # data is not JSON; it's POST form data for proper prefilter form validation logic
            data = request.data.copy()
            evidence_type = get_enum_or_400(
                tryParseInt(request.data.get("evidence_type", -1)), constants.StudyType
            )
            uuid = "zzz-zzz" if settings.IS_TESTING else str(uuid4())
            data.update(title=uuid, slug=uuid, evidence_type=evidence_type)
            form = forms.RoBForm(
                data, evidence_type=evidence_type, visual_type=visual_type, parent=assessment
            )
            if form.is_valid() is False:
                raise ValidationError(form.errors)
            instance = form.save(commit=False)
            return Response(serializers.VisualSerializer(instance).data)

        with PydanticToDjangoError(drf=True):
            config = schemas.VisualDataRequest.model_validate(request.data)
        instance = config.mock_visual(assessment)
        data = instance.get_data()
        return Response(data)


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

    @action(detail=True, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def json_data(self, request, pk):
        """Get json data export for a visual."""
        instance = self.get_object()
        data = instance.get_data()
        return Response(data)


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
        data = cacheable(lambda: ser.get_data(), cache_key)
        return Response(data)
