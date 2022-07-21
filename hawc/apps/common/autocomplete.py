from dal import autocomplete

from django.utils.encoding import force_str
from django.urls import reverse_lazy
from django.http import Http404


class BaseAutocomplete(autocomplete.Select2QuerySetView):
    # AJAX only? `request.is_ajax()`
    # Other permissions?

    @classmethod
    def name(cls):
        app_name = cls.__module__.split(".")[-2].lower()
        class_name = cls.__name__.lower()
        return f"{app_name}-{class_name}"

    @classmethod
    def url(cls):
        # must lazily reverse url to prevent circular imports
        return reverse_lazy("autocomplete", args=[cls.name()])


class AutocompleteRegistry:
    def __init__(self):
        self._registry = {}

    def validate(self, lookup):
        if not issubclass(lookup, BaseAutocomplete):
            raise ValueError("Registered autocompletes must inherit from the BaseAutocomplete class")

    def register(self, lookup):
        self.validate(lookup)
        name = force_str(lookup.name())
        if name in self._registry:
            raise KeyError(f"The name {name} is already registered")
        self._registry[name] = lookup

    def unregister(self, lookup):
        self.validate(lookup)
        name = force_str(lookup.name())
        if name not in self._registry:
            raise KeyError(f"The name {name} is not registered")
        del self._registry[name]

    def get(self, key):
        return self._registry.get(key, None)


registry = AutocompleteRegistry()


def get_autocomplete(request, autocomplete_name):
    autocomplete_cls = registry.get(autocomplete_name)
    if autocomplete_cls is None:
        raise Http404(f"Autocomplete {autocomplete_name} not found")

    return autocomplete_cls.as_view()(request)
