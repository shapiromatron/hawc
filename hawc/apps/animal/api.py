from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    AssessmentViewSet,
    CleanupFieldsBaseViewSet,
    DoseUnitsViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import create_object_log
from . import exports, models, serializers
from .actions.model_metadata import AnimalMetadata
from .actions.term_check import term_check


class AnimalAssessmentViewSet(viewsets.GenericViewSet):
    model = models.Assessment
    queryset = models.Assessment.objects.all()
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_endpoint_queryset(self):
        perms = self.assessment.user_permissions(self.request.user)
        if not perms["edit"]:
            return models.Endpoint.objects.published(self.assessment)
        return models.Endpoint.objects.get_qs(self.assessment)

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
            self.get_endpoint_queryset(),
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
            self.get_endpoint_queryset(),
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
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_study_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-study-heatmap-{self.assessment.id}")
        return Response(export)

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
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_df(self.assessment.id, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-endpoint-heatmap-{self.assessment.id}")
        return Response(export)

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
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_doses_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-endpoint-doses-heatmap-{self.assessment.id}")
        return Response(export)

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
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.objects.endpoint_df(
                self.assessment, published_only=not unpublished
            )
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-endpoint-list-{self.assessment.id}")
        return Response(export)

    @action(
        detail=True,
        url_path="ehv-check",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def ehv_check(self, request, pk):
        _ = self.get_object()
        df = term_check(pk)
        export = FlatExport(df, f"term-report-{pk}")
        return Response(export)


class Experiment(mixins.CreateModelMixin, AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study", "study__assessment", "dtxsid")
            .prefetch_related("study__searches", "study__identifiers")
        )

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
    permission_classes = (AssessmentLevelPermissions,)

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
    permission_classes = (AssessmentLevelPermissions,)

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


class AnimalGroupCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.AnimalGroupCleanupFieldsSerializer
    model = models.AnimalGroup
    assessment_filter_args = "experiment__study__assessment"


class EndpointCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.EndpointCleanupFieldsSerializer
    model = models.Endpoint
    assessment_filter_args = "assessment"


class DosingRegimeCleanupFieldsView(CleanupFieldsBaseViewSet):
    serializer_class = serializers.DosingRegimeCleanupFieldsSerializer
    model = models.DosingRegime
    assessment_filter_args = "dosed_animals__experiment__study__assessment"


class DoseUnits(DoseUnitsViewSet):
    pass


class Metadata(viewsets.ViewSet):
    def list(self, request):
        return AnimalMetadata.handle_request(request)
