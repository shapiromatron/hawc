"""Dynamic Django forms."""
import json

from crispy_forms import layout as cfl
from django import forms

from ..forms import BaseFormHelper
from .schemas import Behavior, Schema


class DynamicForm(forms.Form):
    """Dynamic Django form.

    This is built from a custom schema that defines fields and conditional logic.
    """

    def __init__(self, schema: Schema, *args, **kwargs):
        """Create dynamic form."""
        super().__init__(*args, **kwargs)
        self.schema = schema
        fields = {f.name: f.get_form_field() for f in self.schema.fields}
        self.fields.update(fields)

    @property
    def helper(self):
        """Django crispy form helper."""
        helper = DynamicFormHelper(self)

        # wrap up field inputs with bootstrap grid
        helper.auto_wrap_fields()

        # expose serialized conditions w/ unique id to template
        helper.conditions = [
            {
                "subject_id": self[condition.subject].auto_id,
                "observer_ids": [self[observer].auto_id for observer in condition.observers],
                "comparison": condition.comparison,
                "comparison_value": condition.comparison_value,
                "behavior": condition.behavior,
            }
            for condition in self.schema.conditions
        ]
        helper.conditions_id = f"conditions-{hash(json.dumps(helper.conditions))}"
        helper.layout.append(cfl.HTML("{{ conditions|json_script:conditions_id }}"))

        return helper

    def full_clean(self):
        """Overridden full_clean that handles conditional logic from schema."""
        # handle conditions
        if self.is_bound:
            fields = self.fields.copy()  # copy to restore after clean
            data = self.data.copy()  # copy in case it's immutable
            for condition in self.schema.conditions:
                bf = self[condition.subject]
                value = bf.field.to_python(bf.value())
                check = condition.comparison.compare(value, condition.comparison_value)
                show = check if condition.behavior == Behavior.SHOW else not check
                if not show:
                    for observer in condition.observers:
                        # remove data that should be hidden
                        data.pop(observer, None)
                        # remove fields that should be hidden;
                        # this is restored after clean
                        self.fields.pop(observer)
            self.data = data

        # run default full_clean
        super().full_clean()

        # restore fields
        if self.is_bound:
            self.fields = fields


class DynamicFormHelper(BaseFormHelper):
    """Django crispy form helper."""

    form_tag = False

    def auto_wrap_fields(self):
        """Wrap fields in bootstrap classes."""
        if len(self.form.schema.fields) == 0:
            return

        for field in self.form.schema.fields:
            index = self.layout.index(field.name)
            css_class = field.css_class or "col-12"
            self[index].wrap(cfl.Column, css_class=css_class)

        self[:].wrap_together(cfl.Row)
        self.add_field_wraps()
