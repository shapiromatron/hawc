from typing import ForwardRef, Optional

import django_filters as df
from crispy_forms import layout as cfl
from django import forms
from pydantic import BaseModel, conlist

from . import autocomplete
from .forms import BaseFormHelper, form_actions_apply_filters


def filter_noop(queryset, name, value):
    return queryset


class PaginationFilter(df.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        default_kwargs = dict(
            label="Items per page",
            choices=(
                (25, "25"),
                (50, "50"),
                (100, "100"),
                (250, "250"),
                (500, "500"),
            ),
            method=filter_noop,
        )
        default_kwargs.update(kwargs)
        super().__init__(*args, **default_kwargs)


class AutocompleteModelMultipleChoiceFilter(df.ModelMultipleChoiceFilter):
    field_class = autocomplete.AutocompleteMultipleChoiceField


class AutocompleteModelChoiceFilter(df.ModelChoiceFilter):
    field_class = autocomplete.AutocompleteChoiceField


GridRow = ForwardRef("GridRow")


class GridColumn(BaseModel):
    rows: list[GridRow] = []

    breakpoint: Optional[str]
    width: Optional[int]

    def apply_layout(self, helper, index):
        if self.rows:
            for i, row in enumerate(self.rows):
                row.apply_layout(helper, index + i)
            helper[index : index + len(self.rows)].wrap_together(
                cfl.Column, css_class=self.css_class
            )
        else:
            helper[index].wrap(cfl.Column, css_class=self.css_class)

    @property
    def css_class(self):
        breakpoint = f"-{self.breakpoint}" if self.breakpoint is not None else ""
        width = f"-{self.width}" if self.width is not None else ""
        return f"col{breakpoint}{width}"


class GridRow(BaseModel):
    columns: conlist(GridColumn, min_items=1)

    def apply_layout(self, helper, index):
        for i, column in enumerate(self.columns):
            column.apply_layout(helper, index + i)
        helper[index : index + len(self.columns)].wrap_together(cfl.Row)


GridColumn.update_forward_refs()


class GridLayout(BaseModel):
    rows: conlist(GridRow, min_items=1)

    def apply_layout(self, helper):
        for i, row in enumerate(self.rows):
            row.apply_layout(helper, i)


class FilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        grid_layout = kwargs.pop("grid_layout", None)
        self.grid_layout = GridLayout.parse_obj(grid_layout) if grid_layout is not None else None

        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=form_actions_apply_filters())
        helper.form_method = "GET"

        if self.grid_layout:
            self.grid_layout.apply_layout(helper)

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
    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)

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
        return form
