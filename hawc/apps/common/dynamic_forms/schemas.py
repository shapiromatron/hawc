"""Schemas to build dynamic Django forms."""
from enum import Enum

from django.forms import HiddenInput, JSONField
from pydantic import BaseModel, conlist, field_validator, model_validator

from ..forms import DynamicFormField
from . import fields, forms


class Comparison(str, Enum):
    """Enum for comparisons."""

    __slots__ = ()

    EQUALS = "equals"
    IN = "in"
    CONTAINS = "contains"

    def _equals(self, x, y) -> bool:
        # x equals y
        return x == y

    def _in(self, x, y) -> bool:
        # x (or a subset of x) is in y
        return any(_ in y for _ in x)

    def _contains(self, x, y) -> bool:
        # x contains y
        return set(x) >= set(y)

    def compare(self, x, y) -> bool:
        """Perform comparison based on enum value."""
        x = x if isinstance(x, list) else [x]
        y = y if isinstance(y, list) else [y]
        return getattr(self, f"_{self.value.lower()}")(x, y)


class Behavior(str, Enum):
    """Enum for form field behavior; behavior applies when condition is true."""

    __slots__ = ()

    SHOW = "show"
    HIDE = "hide"


class Condition(BaseModel):
    """Condition that affects the visibility of fields."""

    subject: str
    observers: list[str]
    comparison: Comparison = Comparison.EQUALS
    comparison_value: bool | str | int | conlist(bool | str | int, min_length=1)
    behavior: Behavior = Behavior.SHOW


class Schema(BaseModel):
    """Schema for dynamic form."""

    fields: list[fields.Field]
    conditions: list[Condition] = []

    @model_validator(mode="after")
    def validate_conditions(self):
        """Validate conditions."""
        # condition subjects and observers should be existing fields
        field_names = {field.name for field in self.fields}
        conditions = self.conditions
        subjects = {condition.subject for condition in conditions}
        observers = {observer for condition in conditions for observer in condition.observers}
        if bad_subjects := (subjects - field_names):
            raise ValueError(f"Invalid condition subject(s): {', '.join(bad_subjects)}")
        if bad_observers := (observers - field_names):
            raise ValueError(f"Invalid condition observer(s): {', '.join(bad_observers)}")
        return self

    @field_validator("fields")
    def unique_field_names(cls, v):
        """Validate field names."""
        unique_names = {field.name for field in v}
        if len(unique_names) != len(v):
            raise ValueError("Duplicate field name(s)")
        return v

    def to_form(self, *args, **kwargs):
        """Get dynamic form for this schema."""
        return forms.DynamicForm(self, *args, **kwargs)

    def to_form_field(self, prefix, form_kwargs=None, *args, **kwargs):
        """Get dynamic form field for this schema."""
        if len(self.fields) == 0:
            return JSONField(widget=HiddenInput(), required=False)
        return DynamicFormField(prefix, self.to_form, form_kwargs, *args, **kwargs)
