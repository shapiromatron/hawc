from django.forms.widgets import CheckboxInput
from django.utils import timezone


class DateCheckboxInput(CheckboxInput):
    def value_from_datadict(self, data, files, name):
        # cast the boolean returned to a timestamp or None
        value = super().value_from_datadict(data, files, name)
        return timezone.now() if value else None
