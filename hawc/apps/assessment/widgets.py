from django import forms
from django.utils import timezone


class DateCheckboxInput(forms.widgets.Input):
    input_type = "checkbox"
    template_name = "django/forms/widgets/checkbox.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def check_test(v):
        return not (v is None or v is False or v == "")

    def format_value(self, value):
        """Only return the 'value' attribute if value isn't empty."""
        if value is True or value is False or value is None or value == "":
            return
        return str(value)

    def get_context(self, name, value, attrs):
        if value:
            attrs = {**(attrs or {}), "checked": True}
        return super().get_context(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            return None
        value = data.get(name)
        print(f"!---{value}---!")
        # True creates a datetime value and false returns None.
        values = {"on": timezone.now(), "false": None}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return value

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False
