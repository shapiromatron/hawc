from django import forms

from ...common.filterset import BaseFilterSet
from ...common.forms import BaseFormHelper


class PrefilterForm(forms.Form):
    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper


class PrefilterBaseFilterSet(BaseFilterSet):
    def noop(self, queryset, name, value):
        return queryset

    def _set_passthrough_choices(self, form: forms.Form, field_names: list[str]):
        for field_name in field_names:
            form.fields[field_name].choices = [(v, v) for v in form.data.get(field_name, [])]

    def set_passthrough_options(self, form):
        """Don't set valid queryset choices from db when querying; accept what is saved."""
        raise NotImplementedError("Subclass requires implementation")

    def set_form_options(self, form):
        """Set valid queryset choices when editing a visual."""
        raise NotImplementedError("Subclass requires implementation")
