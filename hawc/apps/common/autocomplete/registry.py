from django.http import Http404
from django.utils.encoding import force_str
from django.utils.module_loading import autodiscover_modules

from .views import BaseAutocomplete


class AutocompleteRegistry:
    def __init__(self):
        self._registry = {}

    def validate(self, lookup):
        if not issubclass(lookup, BaseAutocomplete):
            raise ValueError(
                "Registered autocompletes must inherit from the BaseAutocomplete class"
            )

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

    def get(self, key):
        return self._registry.get(key, None)


registry = AutocompleteRegistry()


def register(Cls):
    registry.register(Cls)
    return Cls


def get_autocomplete(request, autocomplete_name):
    autocomplete_cls = registry.get(autocomplete_name)
    if autocomplete_cls is None:
        raise Http404(f"Autocomplete {autocomplete_name} not found")

    return autocomplete_cls.as_view()(request)


def autodiscover():
    # Attempt to import the autocomplete modules.
    autodiscover_modules("autocomplete", register_to=registry)
