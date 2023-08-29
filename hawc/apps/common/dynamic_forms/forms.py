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

        self[:].wrap_together(cfl.Row, id="row_id_dynamic_form")
        self.add_field_wraps()


class DynamicFormWidget(forms.Widget):
    """Widget to display dynamic form inline."""

    template_name = "common/widgets/dynamic_form.html"

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
