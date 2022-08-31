from dal import autocomplete
from django.conf import settings
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from django.http import Http404, HttpResponseForbidden
from django.utils.encoding import force_str
from django.utils.module_loading import autodiscover_modules

from .helper import reverse_with_query_lazy

## Views


class BaseAutocomplete(autocomplete.Select2QuerySetView):
    filter_fields = []
    order_by = ""
    order_direction = ""

    def get_field(self, obj):
        return getattr(obj, self.field)

    def get_field_result(self, obj):
        return {
            "id": self.get_result_value(obj),
            "text": self.get_field(obj),
            "selected_text": self.get_field(obj),
        }

    def get_result(self, obj):
        return {
            "id": self.get_result_value(obj),
            "text": self.get_result_label(obj),
            "selected_text": self.get_selected_result_label(obj),
        }

    def get_results(self, context):
        return [
            self.get_field_result(obj) if self.field else self.get_result(obj)
            for obj in context["object_list"]
        ]

    def update_qs(self, qs):
        return qs

    @classmethod
    def get_base_queryset(cls, filters: dict = None):
        """
        Gets the base queryset to perform searches on

        Args:
            filters (dict, optional): Field/value pairings to filter queryset on, as long as fields are in class property filter_fields

        Returns:
            QuerySet: Base queryset
        """
        filters = filters or {}
        filters = {key: filters[key] for key in filters if key in cls.filter_fields}
        qs = cls.model.objects.all()
        return qs.filter(**filters)

    def get_queryset(self):
        # get base queryset
        qs = self.get_base_queryset(self.request.GET)

        # check forwarded values for search_fields
        self.search_fields = self.forwarded.get("search_fields") or self.search_fields

        # perform search
        qs = self.get_search_results(qs, self.q)

        if self.field:
            # order by field and get distinct
            qs = qs.order_by(self.field).distinct(self.field)
        else:
            # check forwarded values for ordering
            self.order_by = self.forwarded.get("order_by") or self.order_by
            self.order_direction = self.forwarded.get("order_direction") or self.order_direction
            if self.order_by:
                qs = qs.order_by(self.order_direction + self.order_by)

        return qs

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            pass
            # return HttpResponseForbidden("AJAX required")
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        self.field = request.GET.get("field", "")
        if self.field:
            self.search_fields = [self.field]
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


class SearchLabelMixin:
    """
    Constructs autocomplete labels by using values from the search_fields
    """

    def get_result_label(self, result):
        labels = []
        for path in self.search_fields:
            item = result
            for attribute in path.split("__"):
                item = getattr(item, attribute)
            labels.append(str(item))
        return " | ".join(labels)


## Widgets


class AutocompleteWidgetMixin:
    def __init__(
        self,
        autocomplete_class: BaseAutocomplete,
        filters: dict = None,
        autocomplete_function: str = None,
        *args,
        **kwargs,
    ):
        # set url
        filters = filters or {}
        kwargs["url"] = autocomplete_class.url(**filters)

        # add bootstrap theme to attrs
        attrs = kwargs.get("attrs", {})
        attrs.setdefault("data-theme", "bootstrap")
        attrs.setdefault("data-width", "100%")
        kwargs["attrs"] = attrs

        super().__init__(*args, **kwargs)

        self.filters = filters
        self.autocomplete_class = autocomplete_class
        self.autocomplete_function = autocomplete_function or self.autocomplete_function

    def set_filters(self, filters: dict):
        self.filters = filters
        self.url = self.autocomplete_class.url(**self.filters)

    def update_filters(self, filters: dict):
        self.filters.update(filters)
        self.url = self.autocomplete_class.url(**self.filters)


class AutocompleteSelectWidget(AutocompleteWidgetMixin, autocomplete.ModelSelect2):
    pass


class AutocompleteSelectMultipleWidget(AutocompleteWidgetMixin, autocomplete.ModelSelect2Multiple):
    def __init__(self, *args, **kwargs):
        # remove ability to delete all selections at once
        attrs = kwargs.get("attrs", {})
        attrs.setdefault("data-allow-clear", "false")
        kwargs["attrs"] = attrs

        super().__init__(*args, **kwargs)


class AutocompleteTextWidget(AutocompleteWidgetMixin, autocomplete.Select2):
    autocomplete_function = "select2text"

    class Media:
        js = (f"{settings.STATIC_URL}js/autocomplete_text.js",)

    def __init__(self, field: str, *args, **kwargs):
        # add field to filters
        filters = kwargs.get("filters", {})
        filters.setdefault("field", field)
        kwargs["filters"] = filters
        super().__init__(*args, **kwargs)

    def filter_choices_to_render(self, selected_choices):
        self.choices = [[choice, choice] for choice in selected_choices]


## Form fields
class AutocompleteFieldMixin:
    def __init__(self, autocomplete_class: BaseAutocomplete, filters: dict = None, *args, **kwargs):
        self.autocomplete_class = autocomplete_class
        filters = filters or {}
        kwargs["queryset"] = autocomplete_class.get_base_queryset(filters)

        # use the same labels for initial values that are used by autocomplete
        self.label_from_instance = autocomplete_class().get_result_label

        # determine the widget to use
        if isinstance(self, ModelMultipleChoiceField):
            Widget = AutocompleteSelectMultipleWidget
        elif isinstance(self, ModelChoiceField):
            Widget = AutocompleteSelectWidget
        else:
            raise NotImplementedError()
        kwargs["widget"] = Widget(autocomplete_class=autocomplete_class, filters=filters)

        return super().__init__(*args, **kwargs)

    def set_filters(self, filters: dict):
        self.queryset = self.autocomplete_class.get_base_queryset(filters)
        self.widget.set_filters(filters)


class AutocompleteChoiceField(AutocompleteFieldMixin, ModelChoiceField):
    pass


class AutocompleteMultipleChoiceField(AutocompleteFieldMixin, ModelMultipleChoiceField):
    pass


## Other


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
