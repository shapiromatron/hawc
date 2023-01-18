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
    AssessmentViewset,
    DoseUnitsViewset,
    get_assessment_from_query,
    get_assessment_id_param,
)
from ..assessment.models import Assessment
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    user_can_edit_object,
)
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin, create_object_log
from . import exports, models, serializers
from .actions.model_metadata import AnimalMetadata
from .actions.term_check import term_check


class AnimalAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.Endpoint
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @action(detail=True, url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        """
        Retrieve complete animal data
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        exporter = exports.EndpointGroupFlatComplete(
            self.get_queryset(),
            filename=f"{self.assessment}-bioassay-complete",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())

    @action(detail=True, url_path="endpoint-export", renderer_classes=PandasRenderers)
    def endpoint_export(self, request, pk):
        """
        Retrieve endpoint animal data
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        exporter = exports.EndpointSummary(
            self.get_queryset(),
            filename=f"{self.assessment}-bioassay-summary",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())

    @action(detail=True, url_path="study-heatmap", renderer_classes=PandasRenderers)
    def study_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the study-level (one row per study).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-study-heatmap-pub-{unpublished}"
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_study_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-study-heatmap-{self.assessment.id}")
        return Response(export)

    @action(detail=True, url_path="endpoint-heatmap", renderer_classes=PandasRenderers)
    def endpoint_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the endpoint level (one row per endpoint).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-endpoint-heatmap-unpublished-{unpublished}"
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_df(self.assessment.id, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-endpoint-heatmap-{self.assessment.id}")
        return Response(export)

    @action(detail=True, url_path="endpoint-doses-heatmap", renderer_classes=PandasRenderers)
    def endpoint_doses_heatmap(self, request, pk):
        """
        Return heatmap data with doses for assessment, at the {endpoint + dose unit} level.

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-bioassay-endpoint-doses-heatmap-unpublished-{unpublished}"
        df = cache.get(key)
        if df is None:
            df = models.Endpoint.heatmap_doses_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"bio-endpoint-doses-heatmap-{self.assessment.id}")
        return Response(export)

    @action(detail=True, renderer_classes=PandasRenderers)
    def endpoints(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
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

    @action(detail=True, url_path="ehv-check", renderer_classes=PandasRenderers)
    def ehv_check(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_edit()
        df = term_check(pk)
        export = FlatExport(df, f"term-report-{pk}")
        return Response(export)


class Experiment(mixins.CreateModelMixin, AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study", "study__assessment", "dtxsid")
            .prefetch_related("study__searches", "study__identifiers")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        # permissions check
        user_can_edit_object(serializer.study, self.request.user, raise_exception=True)
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )


class AnimalGroup(mixins.CreateModelMixin, AssessmentViewset):
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


class Endpoint(mixins.CreateModelMixin, AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
    list_actions = ["list", "effects", "rob_filter"]

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

    @action(detail=False)
    def effects(self, request):
        assessment_id = get_assessment_id_param(self.request)
        effects = models.Endpoint.objects.get_effects(assessment_id)
        return Response(effects)

    @action(detail=False)
    def rob_filter(self, request):

        params = request.query_params
        assessment_id = get_assessment_id_param(request)

        query = Q(assessment_id=assessment_id)

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

    @action(detail=False, methods=("post",))
    def update_terms(self, request):
        # check assessment level permissions
        assessment = get_assessment_from_query(request)
        if not assessment.user_can_edit_object(request.user):
            self.permission_denied(request)
        # update endpoint terms (all other validation done in manager)
        updated_endpoints = self.model.objects.update_terms(request.data, assessment)
        serializer = serializers.EndpointSerializer(updated_endpoints, many=True)
        assessment.bust_cache()
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


class DoseUnits(DoseUnitsViewset):
    pass


class Metadata(viewsets.ViewSet):
    def list(self, request):
        return AnimalMetadata.handle_request(request)
