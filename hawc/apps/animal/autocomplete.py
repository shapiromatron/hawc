from ..common.autocomplete import BaseAutocomplete, SearchLabelMixin, register
from . import models


@register
class ExperimentAutocomplete(BaseAutocomplete):
    model = models.Experiment
    search_fields = ["name"]
    filter_fields = ["study_id", "study__assessment_id"]


@register
class AnimalGroupAutocomplete(BaseAutocomplete):
    model = models.AnimalGroup
    search_fields = ["name"]
    filter_fields = ["experiment_id", "experiment__study__assessment_id"]


@register
class EndpointAutocomplete(SearchLabelMixin, BaseAutocomplete):
    paginate_by = 50
    model = models.Endpoint
    search_fields = [
        "animal_group__experiment__study__short_citation",
        "animal_group__experiment__name",
        "animal_group__name",
        "name",
    ]
    filter_fields = [
        "animal_group__experiment__study_id",
        "animal_group__experiment__study__assessment_id",
    ]

    @classmethod
    def get_base_queryset(cls, filters: dict | None = None):
        return super().get_base_queryset(filters).select_related("animal_group__experiment__study")
