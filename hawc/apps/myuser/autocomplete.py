from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class UserAutocomplete(BaseAutocomplete):
    model = models.HAWCUser
    search_fields = ["first_name", "last_name"]
