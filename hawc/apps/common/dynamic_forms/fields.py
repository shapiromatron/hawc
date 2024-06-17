"""Dynamic Django form fields."""

from typing import Annotated, Any, Literal

from django import forms
from django.utils.html import conditional_escape
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic import Field as PydanticField

from . import constants


class _Field(BaseModel):
    """Base class for Django form field schemas.

    This class should only act as a superclass for each specific Django form field.

    Each subclass should add a 'type' property that corresponds with a key
    in constants.FormField, and a 'widget' property that corresponds with keys
    in constants.Widget.
    """

    name: str = PydanticField(pattern=r"^[a-zA-Z0-9_]+$")
    required: bool | None = None
    label: str | None = None
    label_suffix: str | None = None
    initial: Any = None
    help_text: str | None = None
    css_class: str | None = None
    # error_messages
    # validators
    # localize
    # disabled

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("help_text")
    def ensure_safe_string(cls, v):
        """Sanitize help_text values."""
        if v is None:
            return v
        return conditional_escape(v)

    def get_form_field_kwargs(self) -> dict:
        """Get keyword arguments for Django form field."""
        kwargs = self.model_dump(exclude={"type", "widget", "name", "css_class"}, exclude_none=True)
        kwargs["widget"] = constants.Widget[self.widget.upper()].value
        return kwargs

    def get_form_field(self) -> forms.Field:
        """Get Django form field."""
        form_field_cls = constants.FormField[self.type.upper()].value
        form_field_kwargs = self.get_form_field_kwargs()
        return form_field_cls(**form_field_kwargs)

    def get_verbose_name(self) -> str:
        """Get reader friendly name for schema."""
        return self.label or self.name.replace("_", " ").title()


class BooleanField(_Field):
    """Boolean field."""

    type: Literal["boolean"] = "boolean"
    widget: Literal["checkbox_input"] = "checkbox_input"


class CharField(_Field):
    """Character field."""

    type: Literal["char"] = "char"
    widget: Literal["text_input", "textarea"] = "text_input"

    max_length: int | None = None
    min_length: int | None = None
    strip: bool | None = None
    empty_value: str | None = None


class IntegerField(_Field):
    """Integer field."""

    type: Literal["integer"] = "integer"
    widget: Literal["number_input"] = "number_input"

    min_value: int | None = None
    max_value: int | None = None


class FloatField(_Field):
    """Float field."""

    type: Literal["float"] = "float"
    widget: Literal["number_input"] = "number_input"

    min_value: int | None = None
    max_value: int | None = None


class ChoiceField(_Field):
    """Choice field."""

    type: Literal["choice"] = "choice"
    widget: Literal["select", "radio_select"] = "select"

    choices: list[tuple[str, str]]


class YesNoChoiceField(_Field):
    """Yes No field."""

    type: Literal["yes_no"] = "yes_no"
    widget: Literal["radio_select"] = "radio_select"

    choices: list[tuple[Literal["yes", "no"], str]] = [("yes", "Yes"), ("no", "No")]


class MultipleChoiceField(_Field):
    """Multiple choice field."""

    type: Literal["multiple_choice"] = "multiple_choice"
    widget: Literal["select_multiple", "checkbox_select_multiple"] = "select_multiple"

    choices: list[tuple[str, str]]


Field = Annotated[
    BooleanField
    | CharField
    | ChoiceField
    | YesNoChoiceField
    | FloatField
    | IntegerField
    | MultipleChoiceField,
    PydanticField(discriminator="type"),
]
