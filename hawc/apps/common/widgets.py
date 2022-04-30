from random import randint
from typing import Type

from django.forms import ValidationError
from django.forms.widgets import (
    CheckboxInput,
    MultiWidget,
    Select,
    TextInput,
    ChoiceWidget,
    SelectMultiple,
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
        widgets = [
            self.choice_widget(choices=choices, attrs={**attrs, "required": False}),
            TextInput(attrs=attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            in_choices = any(value in v[0] for v in self.choices)
            if in_choices:
                return [value, ""]
            else:
                return [self.other_choice, value]
        return [None, ""]

    def value_from_datadict(self, data, files, name):
        controlled, free_text = super().value_from_datadict(data, files, name)
        if controlled is None and free_text is None:
            return None
        elif controlled != self.other_choice:
            in_choices = any(controlled == v[0] for v in self.choices)
            if not in_choices:
                raise ValidationError("Value not found")
            return controlled
        elif controlled == self.other_choice:
            if free_text:
                return free_text
            elif self.attrs.get("required") is True:
                raise ValidationError("Value required.")
            else:
                return None

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update(jsid=randint(1, 10000), other_choice=self.other_choice)
        return ctx


class SelectOtherWidget(ChoiceOtherWidget):
    choice_widget = Select
    template_name = "common/select_other_widget.html"


class SelectMultipleOtherWidget(ChoiceOtherWidget):
    choice_widget = SelectMultiple
    template_name = "common/select_other_widget.html"
