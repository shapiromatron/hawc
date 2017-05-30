from django.db.models import Q
from assessment.api import AssessmentViewset, DoseUnitsViewset

from . import models, serializers
from utils.api import CleanupFieldsBaseViewSet
from utils.helper import tryParseInt

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable


class Experiment(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer


class AnimalGroup(AssessmentViewset):
    assessment_filter_args = "experiment__study__assessment"
    model = models.AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer


class Endpoint(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
    list_actions = ['list', 'effects', 'rob_filter', ]

    def get_queryset(self):
        return self.model.objects.optimized_qs()

    @list_route()
    def effects(self, request):
        assessment_id = tryParseInt(self.request.query_params.get('assessment_id'), -1)
        effects = models.Endpoint.objects.get_effects(assessment_id)
        return Response(effects)

    @list_route()
    def rob_filter(self, request):
        params = self.request.query_params

        assessment_id = tryParseInt(params.get('assessment_id'), -1)
        query = Q(assessment_id=assessment_id)

        effects = params.get('effect[]')
        if effects:
            query &= Q(effect__in=effects.split(','))

        study_ids = params.get('study_id[]')
        if study_ids:
            query &= Q(animal_group__experiment__study__in=study_ids.split(','))

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


class DoseUnits(DoseUnitsViewset):
    pass
