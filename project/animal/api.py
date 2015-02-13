from __future__ import absolute_import

from api.permissions import AssessmentViewset

from . import models, serializers


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
