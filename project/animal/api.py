from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


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

    def get_queryset(self):
        return self.model.objects.all()\
            .select_related(
                'animal_group',
                'animal_group__dosed_animals',
                'animal_group__experiment',
                'animal_group__experiment__study',
            ).prefetch_related(
                'endpoint_group',
                'effects',
                'animal_group__dosed_animals__doses',
            )
