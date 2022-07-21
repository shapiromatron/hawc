from ..common.autocomplete import BaseAutocomplete, registry
from . import models


class UserAutocomplete(BaseAutocomplete):
    model = models.HAWCUser
    search_fields = ["first_name", "last_name"]


registry.register(UserAutocomplete)
