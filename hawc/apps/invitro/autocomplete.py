from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class IVChemicalAutocomplete(BaseAutocomplete):
    model = models.IVChemical
    search_fields = ["name"]
    filter_fields = ["study__assessment_id"]


@register
class IVCellTypeAutocomplete(BaseAutocomplete):
    model = models.IVCellType
    search_fields = ["cell_type"]
    filter_fields = ["study__assessment_id"]


@register
class IVExperimentAutocomplete(BaseAutocomplete):
    model = models.IVExperiment
    search_fields = ["name"]
    filter_fields = ["study__assessment_id"]


@register
class IVEndpointAutocomplete(BaseAutocomplete):
    model = models.IVEndpoint
    search_fields = ["short_description"]
    filter_fields = ["experiment__study__assessment_id"]
