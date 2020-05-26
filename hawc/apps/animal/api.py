from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    AssessmentViewset,
    DoseUnitsViewset,
    get_assessment_id_param,
)
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet, LegacyAssessmentAdapterMixin
from ..common.helper import re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from . import exports, models, serializers


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

    @action(detail=True, methods=("get",), url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        """
        Retrieve complete animal data
        """
        self.set_legacy_attr(pk)
        exporter = exports.EndpointGroupFlatComplete(
            self.get_queryset(),
            filename=f"{self.assessment}-bioassay-complete",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())

    @action(
        detail=True, methods=("get",), url_path="endpoint-export", renderer_classes=PandasRenderers
    )
    def endpoint_export(self, request, pk):
        """
        Retrieve endpoint animal data
        """
        self.set_legacy_attr(pk)
        exporter = exports.EndpointSummary(
            self.get_queryset(),
            filename=f"{self.assessment}-bioassay-summary",
            assessment=self.assessment,
        )
        return Response(exporter.build_export())


class Experiment(mixins.CreateModelMixin, AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer


class AnimalGroup(mixins.CreateModelMixin, AssessmentViewset):
    assessment_filter_args = "experiment__study__assessment"
    model = models.AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer


class Endpoint(mixins.CreateModelMixin, AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
    list_actions = [
        "list",
        "effects",
        "rob_filter",
    ]

    def get_queryset(self):
        return self.model.objects.optimized_qs()

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
