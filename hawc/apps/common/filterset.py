from typing import ForwardRef

import django_filters as df
from crispy_forms import layout as cfl
from django import forms
from pydantic import BaseModel, conlist

from ..assessment.models import Assessment
from . import autocomplete
from .forms import (
    BaseFormHelper,
    ExpandableFilterFormHelper,
    InlineFilterFormHelper,
    form_actions_apply_filters,
)


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

    breakpoint: str = ""
    width: int | None
    extra_css: str = ""

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
        breakpoint = f"-{self.breakpoint}" if self.breakpoint else ""
        width = f"-{self.width}" if self.width is not None else ""
        extra = f" {self.extra_css}" if self.extra_css else ""
        return f"col{breakpoint}{width}{extra}"


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


class InlineFilterForm(forms.Form):
    """Form model used for inline filterset forms."""

    helper_class = InlineFilterFormHelper

    def __init__(self, *args, **kwargs):
        """Grabs grid_layout kwarg and passes it to GridLayout to apply the layout."""
        layout = kwargs.pop("grid_layout", None)
        self.grid_layout = GridLayout.parse_obj(layout) if layout else None
        self.main_field = kwargs.pop("main_field", None)
        self.appended_fields = kwargs.pop("appended_fields", [])
        self.dynamic_fields = kwargs.pop("dynamic_fields", [])
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        """Helper method for setting up the form."""
        helper = self.helper_class(
            self,
            main_field=self.main_field,
            appended_fields=self.appended_fields,
        )
        helper.form_method = "GET"
        return helper


class ExpandableFilterForm(InlineFilterForm):
    """Form model used for expandable inline filterset forms."""

    helper_class = ExpandableFilterFormHelper

    is_expanded = forms.CharField(initial="false", widget=forms.HiddenInput())

    def clean(self):
        """Remove 'is_expanded' from form data before data is used for filtering."""
        cleaned_data = super().clean()
        cleaned_data.pop("is_expanded", None)


class FilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        grid_layout = kwargs.pop("grid_layout", None)
        self.grid_layout = GridLayout.parse_obj(grid_layout) if grid_layout is not None else None
        self.dynamic_fields = kwargs.pop("dynamic_fields", None)
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=form_actions_apply_filters())
        helper.form_method = "GET"

        if self.grid_layout:
            self.grid_layout.apply_layout(helper)

        return helper


class BaseFilterSet(df.FilterSet):
    def __init__(self, *args, assessment: Assessment | None = None, form_kwargs=None, **kwargs):
        self.assessment = assessment
        super().__init__(*args, **kwargs)
        self.form_kwargs = form_kwargs or {}
        if "grid_layout" not in form_kwargs and hasattr(self.Meta, "grid_layout"):
            self.form_kwargs.update(grid_layout=self.Meta.grid_layout)

    @property
    def perms(self):
        return self.assessment.user_permissions(self.request.user)

    @property
    def form(self):
        if not hasattr(self, "_form"):
            self._form = self.create_form()
        return self._form

    def create_form(self):
        form_class = self.get_form_class()
        if self.is_bound:
            form = form_class(self.data, prefix=self.form_prefix, **self.form_kwargs)
        else:
            form = form_class(prefix=self.form_prefix, **self.form_kwargs)
        if form.dynamic_fields:
            for field in list(form.fields.keys()):
                if field not in form.dynamic_fields and field != "is_expanded":
                    form.fields.pop(field)
        return form
