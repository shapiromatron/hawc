from dal import autocomplete
from dal_select2.widgets import I18N_PATH, ModelSelect2
from django.conf import settings
from django.forms import Media, ModelChoiceField, ModelMultipleChoiceField

from .views import BaseAutocomplete


class HawcModelSelect2(ModelSelect2):
    def __init__(self, *args, **kw):
        attrs = kw.get("attrs", {})
        attrs.setdefault("data-theme", "bootstrap")
        attrs.setdefault("data-width", "100%")
        super().__init__(*args, **kw)


class AutocompleteWidgetMixin:
    @property
    def media(self):
        """Return JS/CSS resources for the widget."""
        extra = "" if settings.DEBUG else ".min"
        i18n_name = self._get_language_code()
        i18n_file = (f"{I18N_PATH}{i18n_name}.js",) if i18n_name else ()

        return Media(
            js=(
                "admin/js/vendor/select2/select2.full.js",
                f"{settings.STATIC_URL}patched/dal/3.9.4/js/autocomplete_light.js",
                f"autocomplete_light/select2{extra}.js",
                f"{settings.STATIC_URL}patched/dal/3.9.4/js/select2text.js",
                *i18n_file,
            ),
            css={
                "screen": (
                    f"admin/css/vendor/select2/select2{extra}.css",
                    "admin/css/autocomplete.css",
                    "autocomplete_light/select2.css",
                    f"{settings.STATIC_URL}patched/dal/3.9.4/css/select2-bootstrap.css",
                ),
            },
        )

    def __init__(
        self,
        autocomplete_class: type[BaseAutocomplete],
        filters: dict | None = None,
        autocomplete_function: str | None = None,
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

    def filter_choices_to_render(self, selected_choices):
        """Filter out un-selected choices if choices is a QuerySet.

        patched - see https://github.com/yourlabs/django-autocomplete-light/pull/1321
        """
        try:
            qs = self.choices.queryset.filter(pk__in=[c for c in selected_choices if c])
        except ValueError:
            # set queryset to empty set if filters are invalid
            qs = self.choices.queryset.none()
        self.choices.queryset = qs


class AutocompleteSelectWidget(AutocompleteWidgetMixin, autocomplete.ModelSelect2):
    pass


class AutocompleteSelectMultipleWidget(AutocompleteWidgetMixin, autocomplete.ModelSelect2Multiple):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        # remove ability to delete all selections at once
        attrs.setdefault("data-allow-clear", "false")
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class AutocompleteTextWidget(AutocompleteWidgetMixin, autocomplete.Select2):
    autocomplete_function = "select2text"

    def __init__(self, field: str, *args, **kwargs):
        # add field to filters
        filters = kwargs.get("filters", {})
        filters.setdefault("field", field)
        kwargs["filters"] = filters
        super().__init__(*args, **kwargs)

    def filter_choices_to_render(self, selected_choices):
        self.choices = [[choice, choice] for choice in selected_choices]


class AutocompleteFieldMixin:
    def __init__(
        self,
        autocomplete_class: type[BaseAutocomplete],
        filters: dict | None = None,
        *args,
        **kwargs,
    ):
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
