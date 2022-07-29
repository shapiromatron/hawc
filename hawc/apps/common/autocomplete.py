from dal import autocomplete
from django.http import Http404, HttpResponseForbidden
from django.utils.encoding import force_str

from .helper import reverse_with_query_lazy


class BaseAutocomplete(autocomplete.Select2QuerySetView):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseForbidden("AJAX required")
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def registry_key(cls):
        app_name = cls.__module__.split(".")[-2].lower()
        class_name = cls.__name__.lower()
        return f"{app_name}-{class_name}"

    @classmethod
    def url(cls, **kwargs):
        # must lazily reverse url to prevent circular imports
        return reverse_with_query_lazy("autocomplete", args=[cls.registry_key()], query=kwargs)


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        # add bootstrap theme to attrs
        attrs = kwargs.get("attrs", {})
        attrs["data-theme"] = "bootstrap"
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class AutocompleteSelectWidget(BootstrapMixin, autocomplete.ModelSelect2):
    pass


class AutocompleteSelectMultipleWidget(BootstrapMixin, autocomplete.ModelSelect2Multiple):
    pass


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
