from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class ChemicalAutocomplete(BaseAutocomplete):
    model = models.Chemical
    search_fields = ["name"]


@register
class ExposureLevelAutocomplete(BaseAutocomplete):
    model = models.ExposureLevel
    search_fields = ["name"]


@register
class OutcomeAutocomplete(BaseAutocomplete):
    model = models.Outcome
    search_fields = ["endpoint"]


@register
class DataExtractionAutocomplete(BaseAutocomplete):
    model = models.DataExtraction
    search_fields = ["comments"]
