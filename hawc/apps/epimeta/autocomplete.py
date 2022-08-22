from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class MetaResultAutocomplete(BaseAutocomplete):
    model = models.MetaResult
    search_fields = ["label"]
    filter_fields = ["protocol_id"]
