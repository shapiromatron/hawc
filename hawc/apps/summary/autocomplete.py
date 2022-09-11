from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class DataPivotAutocomplete(BaseAutocomplete):
    model = models.DataPivot
    search_fields = ["title"]
    filter_fields = ["assessment_id"]


@register
class VisualAutocomplete(BaseAutocomplete):
    model = models.Visual
    search_fields = ["title"]
    filter_fields = ["assessment_id"]
