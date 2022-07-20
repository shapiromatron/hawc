from dal import autocomplete

from . import models


class UserAutocomplete(autocomplete.Select2QuerySetView):
    model = models.HAWCUser
    search_fields = ["first_name", "last_name"]
