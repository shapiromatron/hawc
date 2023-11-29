import pandas as pd
from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentViewSet,
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
    DoseUnitsViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..common.api.utils import get_published_only
from ..common.helper import FlatExport, cacheable
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import create_object_log
from . import exports, models, serializers
from .actions.model_metadata import AnimalMetadata
from .actions.term_check import term_check


class AnimalAssessmentViewSet(BaseAssessmentViewSet):
    model = models.Assessment
    serializer_class = UnusedSerializer

    def get_endpoint_queryset(self, request):
        published_only = get_published_only(self.assessment, request)
        return models.Endpoint.objects.get_qs(self.assessment).published_only(
            self.assessment, published_only
        )

    @action(
        detail=True,
        url_path="full-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def full_export(self, request, pk):
        """
        Retrieve complete animal data
        """
        self.assessment = self.get_object()
        exporter = exports.EndpointGroupFlatComplete(
            self.get_endpoint_queryset(request),
            filename=f"{self.assessment}-bioassay-complete",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())

    @action(
        detail=True,
        url_path="endpoint-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def endpoint_export(self, request, pk):
        """
        Retrieve endpoint animal data
        """
        self.assessment = self.get_object()
        exporter = exports.EndpointSummary(
            self.get_endpoint_queryset(request),
            filename=f"{self.assessment}-bioassay-summary",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())

    @action(
        detail=True,
        url_path="study-heatmap",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def study_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the study-level (one row per study).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.assessment = self.get_object()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_reviewer_or_higher(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-study-heatmap-pub-{unpublished}"

        def func() -> pd.DataFrame:
            return models.Endpoint.heatmap_study_df(self.assessment, published_only=not unpublished)

        df = cacheable(func, key)
        return FlatExport.api_response(df=df, filename=f"bio-study-heatmap-{self.assessment.id}")

    @action(
        detail=True,
        url_path="endpoint-heatmap",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def endpoint_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the endpoint level (one row per endpoint).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.assessment = self.get_object()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_reviewer_or_higher(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-endpoint-heatmap-unpublished-{unpublished}"

        def df_func() -> pd.DataFrame:
            return models.Endpoint.heatmap_df(self.assessment.id, published_only=not unpublished)

        df = cacheable(df_func, key)
        return FlatExport.api_response(df=df, filename=f"bio-endpoint-heatmap-{self.assessment.id}")

    @action(
        detail=True,
        url_path="endpoint-doses-heatmap",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def endpoint_doses_heatmap(self, request, pk):
        """
        Return heatmap data with doses for assessment, at the {endpoint + dose unit} level.

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.assessment = self.get_object()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_reviewer_or_higher(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-endpoint-doses-heatmap-unpublished-{unpublished}"

        def df_func() -> pd.DataFrame:
            return models.Endpoint.heatmap_doses_df(self.assessment, published_only=not unpublished)

        df = cacheable(df_func, key)
        return FlatExport.api_response(
            df=df, filename=f"bio-endpoint-doses-heatmap-{self.assessment.id}"
        )

    @action(
        detail=True,
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def endpoints(self, request, pk):
        self.assessment = self.get_object()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_reviewer_or_higher(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-endpoint-list"

        def df_func() -> pd.DataFrame:
            return models.Endpoint.objects.endpoint_df(
                self.assessment, published_only=not unpublished
            )

        df = cacheable(df_func, key)
        return FlatExport.api_response(df=df, filename=f"bio-endpoint-list-{self.assessment.id}")

    @action(
        detail=True,
        url_path="ehv-check",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def ehv_check(self, request, pk):
        _ = self.get_object()
        df = term_check(pk)
        return FlatExport.api_response(df, f"term-report-{pk}")


class Experiment(mixins.CreateModelMixin, AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study", "study__assessment", "dtxsid")
            .prefetch_related("study__searches", "study__identifiers")
        ).order_by("id")

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )


class AnimalGroup(mixins.CreateModelMixin, AssessmentViewSet):
    assessment_filter_args = "experiment__study__assessment"
    model = models.AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kwargs = {"context": self.get_serializer_context()}

        # build dosing regime first if needed
        dosed_animals = False
        if "dosing_regime" in request.data:
            dosed_animals = True
            dr_serializer = serializers.DosingRegimeSerializer(
                data=request.data.pop("dosing_regime"), **kwargs
            )
            dr_serializer.is_valid(raise_exception=True)
            dosing_regime = dr_serializer.save()
            request.data["dosing_regime_id"] = dosing_regime.id

        # build animal-group
        serializer = serializers.AnimalGroupSerializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        animal_group = serializer.save()
        if dosed_animals:
            # save reverse relation
            dosing_regime.dosed_animals = animal_group
            dosing_regime.save()

        # refresh serializer instance and return
        instance = self.model.objects.get(id=animal_group.id)
        serializer = self.get_serializer(instance)

        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Endpoint(mixins.CreateModelMixin, AssessmentViewSet):
    assessment_filter_args = "assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
    list_actions = ["list", "effects", "rob_filter", "update_terms"]

    def get_queryset(self):
        return self.model.objects.optimized_qs()

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    @action(detail=False, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def effects(self, request):
        effects = models.Endpoint.objects.get_effects(self.assessment.id)
        return Response(effects)

    @action(detail=False, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def rob_filter(self, request):
        params = request.query_params

        query = Q(assessment=self.assessment)

        effects = params.get("effect[]")
        if effects:
            query &= Q(effect__in=effects.split(","))

        study_ids = params.get("study_id[]")
        if study_ids:
            query &= Q(animal_group__experiment__study__in=study_ids.split(","))

        qs = models.Endpoint.objects.filter(query)

        if qs.count() > 100:
            raise NotAcceptable("Must contain < 100 endpoints")

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=("post",), action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT
    )
    def update_terms(self, request):
        # update endpoint terms (all other validation done in manager)
        updated_endpoints = self.model.objects.update_terms(request.data, self.assessment)
        serializer = serializers.EndpointSerializer(updated_endpoints, many=True)
        self.assessment.bust_cache()
        return Response(serializer.data)


class ExperimentCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ExperimentCleanupFieldsSerializer
    model = models.Experiment
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")


class AnimalGroupCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.AnimalGroupCleanupFieldsSerializer
    model = models.AnimalGroup
    assessment_filter_args = "experiment__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("experiment__study")


class EndpointCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.EndpointCleanupFieldsSerializer
    model = models.Endpoint
    assessment_filter_args = "assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("animal_group__experiment__study")


class DosingRegimeCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.DosingRegimeCleanupFieldsSerializer
    model = models.DosingRegime
    assessment_filter_args = "dosed_animals__experiment__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("dosed_animals__experiment__study")


class DoseUnits(DoseUnitsViewSet):
    pass


class Metadata(viewsets.ViewSet):
    def list(self, request):
        return AnimalMetadata.handle_request(request)
