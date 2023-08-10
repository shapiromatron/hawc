from random import randint
import json

from django.conf import settings
from django.forms import ValidationError
from django.forms.widgets import (
    CheckboxInput,
    ChoiceWidget,
    MultiWidget,
    Select,
    SelectMultiple,
    Textarea,
    TextInput,
    Widget
)
from django.utils import timezone


class DateCheckboxInput(CheckboxInput):
    def value_from_datadict(self, data, files, name):
        # cast the boolean returned to a timestamp or None
        value = super().value_from_datadict(data, files, name)
        return timezone.now() if value else None


class ChoiceOtherWidget(MultiWidget):
    """A widget for using a selected value, or specifying custom"""

    choice_widget: type[ChoiceWidget]

    def __init__(self, choices, other_choice: str = "other", attrs=None):
        if attrs is None:
            attrs = {}
        self.other_choice = other_choice
        self.attrs = attrs
        attrs.update(required=False)
        self.choices = choices
        self.allow_multiple_selected = self.choice_widget.allow_multiple_selected
        widgets = [
            self.choice_widget(choices=choices, attrs={**attrs, "required": False}),
            TextInput(attrs=attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        choices = {v[0] for v in self.choices}
        if self.allow_multiple_selected:
            if not value:
                return [[], ""]
            if isinstance(value, str):
                value = [v for v in [el.strip() for el in value.split(",")] if v]
            in_choices = [v for v in value if v in choices]
            not_in_choices = ", ".join([v for v in value if v not in choices])
            if not_in_choices:
                in_choices.append(self.other_choice)
            return [in_choices, not_in_choices]
        else:
            if not value:
                return [None, ""]
            in_choices = value in choices
            return [value, ""] if in_choices else [self.other_choice, value]

    def value_from_datadict(self, data, files, name):
        choices = {v[0] for v in self.choices}
        controlled, free_text = super().value_from_datadict(data, files, name)
        if controlled is None and free_text is None:
            return None
        if self.allow_multiple_selected:
            items = [value for value in controlled if value != self.other_choice]
            has_other = any(value == self.other_choice for value in controlled)
            if has_other and free_text:
                free_items = [el.strip() for el in free_text.split(",")]
                for item in free_items:
                    if item:
                        items.append(item)
            if not items:
                return None
            return items
        else:
            if controlled != self.other_choice:
                in_choices = controlled in choices
                if not in_choices:
                    raise ValidationError("Value not found")
                return controlled
            elif controlled == self.other_choice:
                if free_text:
                    return free_text.strip()
                elif self.attrs.get("required") is True:
                    raise ValidationError("Value required.")
                else:
                    return None

    def format_value(self, value) -> list[str]:
        """Return selected values as a list."""
        if value is None:
            return []
        return value.split(",")

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update(jsid=randint(1, 99999), other_choice=self.other_choice)  # noqa: S311
        return ctx


class SelectOtherWidget(ChoiceOtherWidget):
    choice_widget = Select
    template_name = "common/select_other_widget.html"


class SelectMultipleOtherWidget(ChoiceOtherWidget):
    choice_widget = SelectMultiple
    template_name = "common/select_other_widget.html"


class QuillWidget(Textarea):
    """
    Uses the Quill text editor for input.
    Cleaning is done to remove invalid styles and tags; all inner text is kept.
    """

    class Media:
        js = (f"{settings.STATIC_URL}js/quilltext.js",)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        class_name = attrs.get("class")
        attrs["class"] = class_name + " quilltext" if class_name else "quilltext"
        return attrs

class DynamicFormWidget(Widget):
    """Widget to display dynamic form inline."""

    template_name = "common/dynamic_form.html"

    def __init__(self, prefix, form_class, form_kwargs=None, *args, **kwargs):
        """Create dynamic form widget."""
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.form_class = form_class
        if form_kwargs is None:
            form_kwargs = {}
        self.form_kwargs = {"prefix": prefix, **form_kwargs}

    def add_prefix(self, field_name):
        """Add prefix in the same way Django forms add prefixes."""
        return f"{self.prefix}-{field_name}"

    def format_value(self, value):
        """Value used in rendering."""
        value = json.loads(value)
        if value:
            value = {self.add_prefix(k): v for k, v in value.items()}
        return self.form_class(data=value, **self.form_kwargs)

    def value_from_datadict(self, data, files, name):
        """Parse value from POST request."""
        form = self.form_class(data=data, **self.form_kwargs)
        form.full_clean()
        return form.cleaned_data