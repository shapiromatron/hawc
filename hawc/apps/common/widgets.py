from random import randint

from django.forms import ValidationError
from django.forms.widgets import CheckboxInput, MultiWidget, Select, TextInput
from django.utils import timezone


class DateCheckboxInput(CheckboxInput):
    def value_from_datadict(self, data, files, name):
        # cast the boolean returned to a timestamp or None
        value = super().value_from_datadict(data, files, name)
        return timezone.now() if value else None


class SelectOtherWidget(MultiWidget):
    """A widget for using a selected value, or specifying custom"""

    template_name = "common/select_other_widget.html"
    OTHER = "other"

    def __init__(self, choices, attrs=None):
        if attrs is None:
            attrs = {}
        self.attrs = attrs
        attrs.update(required=False)
        self.choices = choices
        widgets = [
            Select(choices=choices, attrs={**attrs, "required": False}),
            TextInput(attrs=attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            in_choices = any(value in v[0] for v in self.choices)
            if in_choices:
                return [value, ""]
            else:
                return [self.OTHER, value]
        return [None, ""]

    def value_from_datadict(self, data, files, name):
        controlled, free_text = super().value_from_datadict(data, files, name)
        if controlled is None and free_text is None:
            return None
        elif controlled != self.OTHER:
            in_choices = any(controlled == v[0] for v in self.choices)
            if not in_choices:
                raise ValidationError("Value not found")
            return controlled
        elif controlled == self.OTHER:
            if free_text:
                return free_text
            if not free_text and self.attrs.get("required") is True:
                raise ValidationError("Value required.")

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update(uuid=randint(1, 1000))
        return ctx
