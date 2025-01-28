from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class VisualAutocomplete(BaseAutocomplete):
    model = models.Visual
    search_fields = ["title"]
    filter_fields = ["assessment_id"]
