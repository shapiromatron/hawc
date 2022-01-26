from django import forms
from django.utils import timezone


class DateCheckboxInput(forms.widgets.CheckboxInput):
    def value_from_datadict(self, data, files, name):
        if name not in data:
            return None
        value = data.get(name)
        # True creates a datetime value and false returns None.
        values = {"on": timezone.now(), "false": None}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return value
