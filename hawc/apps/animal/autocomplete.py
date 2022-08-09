from ..common.autocomplete import BaseAutocomplete, SearchLabelMixin, register
from . import models


@register
class ExperimentAutocomplete(BaseAutocomplete):
    model = models.Experiment
    search_fields = ["name"]
    filter_fields = ["study_id"]


@register
class AnimalGroupAutocomplete(BaseAutocomplete):
    model = models.AnimalGroup
    search_fields = ["name"]
    filter_fields = ["experiment_id"]


@register
class EndpointAutocomplete(SearchLabelMixin, BaseAutocomplete):
    model = models.Endpoint
    filter_fields = ["study_id"]

    @classmethod
    def get_base_queryset(cls, filters: dict = None):
        return super().get_base_queryset(filters).select_related("animal_group__experiment")
