from ..common.autocomplete import BaseAutocomplete, register
from . import models

@register
class ExperimentAutocomplete(BaseAutocomplete):
    model = models.Experiment
    search_fields = ["guideline_name_number"]


@register
class ChemicalAutocomplete(BaseAutocomplete):
    model = models.Chemical
    search_fields = ["name", "cas"]

