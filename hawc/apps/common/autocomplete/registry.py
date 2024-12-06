from django.core.exceptions import FieldError, ValidationError
from django.http import Http404
from django.http.response import HttpResponseBadRequest
from django.utils.encoding import force_str
from django.utils.module_loading import autodiscover_modules

from .views import BaseAutocomplete


class AutocompleteRegistry:
    def __init__(self):
        self._registry: dict[str, type[BaseAutocomplete]] = {}

    def validate(self, lookup):
        if not issubclass(lookup, BaseAutocomplete):
            raise ValueError("Must inherit from the BaseAutocomplete class")

    def register(self, lookup):
        self.validate(lookup)
        key = force_str(lookup.registry_key())
        if key in self._registry:
            raise KeyError(f"The key {key} is already registered")
        self._registry[key] = lookup

    def unregister(self, lookup):
        self.validate(lookup)
        key = force_str(lookup.registry_key())
        if key not in self._registry:
            raise KeyError(f"The key {key} is not registered")
        del self._registry[key]

    def get(self, key) -> type[BaseAutocomplete]:
        try:
            return self._registry[key]
        except KeyError as err:
            raise ValueError(f"Key not found: {key}") from err


registry = AutocompleteRegistry()


def register(Cls):
    registry.register(Cls)
    return Cls


def get_autocomplete(request, autocomplete_name):
    try:
        autocomplete_cls = registry.get(autocomplete_name)
    except ValueError as err:
        raise Http404(f"Autocomplete {autocomplete_name} not found") from err
    try:
        return autocomplete_cls.as_view()(request)
    except (ValueError, ValidationError, FieldError):
        return HttpResponseBadRequest("Bad request.")


def autodiscover():
    autodiscover_modules("autocomplete", register_to=registry)
