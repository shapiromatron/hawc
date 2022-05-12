from random import randint
from typing import List, Type

from django.forms import ValidationError
from django.forms.widgets import (
    CheckboxInput,
    ChoiceWidget,
    MultiWidget,
    Select,
    SelectMultiple,
    TextInput,
)
from django.utils import timezone


class DateCheckboxInput(CheckboxInput):
    def value_from_datadict(self, data, files, name):
        # cast the boolean returned to a timestamp or None
        value = super().value_from_datadict(data, files, name)
        return timezone.now() if value else None


class ChoiceOtherWidget(MultiWidget):
    """A widget for using a selected value, or specifying custom"""

    choice_widget: Type[ChoiceWidget]

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

    def format_value(self, value) -> List[str]:
        """Return selected values as a list."""
        if value is None:
            return []
        return value.split(",")

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update(jsid=randint(1, 99999), other_choice=self.other_choice)
        return ctx


class SelectOtherWidget(ChoiceOtherWidget):
    choice_widget = Select
    template_name = "common/select_other_widget.html"


class SelectMultipleOtherWidget(ChoiceOtherWidget):
    choice_widget = SelectMultiple
    template_name = "common/select_other_widget.html"
