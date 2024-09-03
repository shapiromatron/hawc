from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class SearchAutocomplete(BaseAutocomplete):
    model = models.Search
    filter_fields = ["assessment_id"]
    search_fields = ["title"]
