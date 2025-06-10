from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class ChemicalAutocomplete(BaseAutocomplete):
    model = models.Chemical
    search_fields = ["name"]
