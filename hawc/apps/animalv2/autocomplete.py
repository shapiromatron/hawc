from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class ChemicalAutocomplete(BaseAutocomplete):
    model = models.Chemical
    search_fields = ["name"]


@register
class ExperimentAutocomplete(BaseAutocomplete):
    model = models.Experiment
    search_fields = ["name"]
    filter_fields = ["study_id", "study__assessment_id"]
