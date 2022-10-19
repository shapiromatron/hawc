import django_filters as df
from crispy_forms import layout as cfl
from django import forms

from . import autocomplete
from .forms import BaseFormHelper, form_actions_apply_filters


class AutocompleteModelMultipleChoiceFilter(df.ModelMultipleChoiceFilter):
    field_class = autocomplete.AutocompleteMultipleChoiceField


class AutocompleteModelChoiceFilter(df.ModelChoiceFilter):
    field_class = autocomplete.AutocompleteChoiceField


class FilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.grid_layout = kwargs.pop("grid_layout", [])
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=form_actions_apply_filters())
        helper.form_method = "GET"

        for i, row in enumerate(self.grid_layout):
            for j, column in enumerate(row):
                helper[i + j].wrap(cfl.Column, css_class=f"col-md-{column}")
            helper[i : i + len(row)].wrap_together(cfl.Row)

        return helper


class FilterSetOptions:
    def __init__(self, options=None):
        self.model = getattr(options, "model", None)
        self.fields = getattr(options, "fields", None)
        self.exclude = getattr(options, "exclude", None)

        self.filter_overrides = getattr(options, "filter_overrides", {})
        self.field_kwargs = getattr(options, "field_kwargs", {})
        self.grid_layout = getattr(options, "grid_layout", [])

        self.form = getattr(options, "form", FilterForm)


class FilterSetMetaclass(df.filterset.FilterSetMetaclass):
    def __new__(cls, name, bases, attrs):
        attrs["declared_filters"] = cls.get_declared_filters(bases, attrs)

        new_class = type.__new__(cls, name, bases, attrs)
        new_class._meta = FilterSetOptions(getattr(new_class, "Meta", None))
        new_class.base_filters = new_class.get_filters()

        for filter_name, field_kwargs in new_class._meta.field_kwargs.items():
            new_class.base_filters[filter_name].extra.update(field_kwargs)

        return new_class


class FilterSet(df.filterset.BaseFilterSet, metaclass=FilterSetMetaclass):
    pass


class BaseFilterSet(FilterSet):
    paginate_by = df.ChoiceFilter(
        label="Items per page",
        choices=(
            (25, "25"),
            (50, "50"),
            (100, "100"),
            (250, "250"),
            (500, "500"),
        ),
        method="filter_noop",
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)

    def filter_noop(self, queryset, name, value):
        return queryset

    @property
    def perms(self):
        return self.assessment.user_permissions(self.request.user)

    @property
    def form(self):
        if not hasattr(self, "_form"):
            Form = self.get_form_class()
            if self.is_bound:
                form = Form(self.data, prefix=self.form_prefix, grid_layout=self._meta.grid_layout)
            else:
                form = Form(prefix=self.form_prefix, grid_layout=self._meta.grid_layout)
            self._form = self.change_form(form)
        return self._form

    def prefilter_queryset(self, queryset):
        # any prefiltering or annotations necessary for ordering go here
        pass

    def filter_queryset(self, queryset):
        queryset = self.prefilter_queryset(queryset)
        return super().filter_queryset(queryset)

    def change_form(self, form):
        pass
