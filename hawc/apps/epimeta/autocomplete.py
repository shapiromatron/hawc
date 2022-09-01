from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class MetaResultAutocomplete(BaseAutocomplete):
    model = models.MetaResult
    search_fields = ["label"]
    filter_fields = ["protocol_id", "protocol__study__assessment_id"]


@register
class MetaProtocolAutocomplete(BaseAutocomplete):
    model = models.MetaProtocol
    search_fields = ["name"]
    filter_fields = ["study__assessment_id"]
