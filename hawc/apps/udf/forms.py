from crispy_forms import bootstrap as cfb
from crispy_forms import layout as cfl
from django import forms
from django.urls import reverse, reverse_lazy

from hawc.apps.common.autocomplete.forms import AutocompleteSelectMultipleWidget
from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import BaseFormHelper, PydanticValidator, TextareaButton
from hawc.apps.myuser.autocomplete import UserAutocomplete

from .models import UserDefinedForm


class UDFForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).dict(),
        validators=[PydanticValidator(Schema)],
        widget=TextareaButton(
            btn_attrs={
                "hx-post": reverse_lazy("udf:schema_preview"),
                "hx-target": "#schema-preview-frame",
                "hx-swap": "innerHTML",
                "class": "ml-2",
            },
            btn_content="Preview",
            btn_stretch=False,
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            self.instance.creator = user

    class Meta:
        model = UserDefinedForm
        fields = ("name", "description", "schema", "editors", "deprecated")
        widgets = {
            "editors": AutocompleteSelectMultipleWidget(UserAutocomplete),
        }

    @property
    def helper(self):
        self.fields["description"].widget.attrs["rows"] = 3
        cancel_url = reverse("udf:udf_list")
        form_actions = [
            cfl.Submit("save", "Save"),
            cfl.HTML(f'<a role="button" class="btn btn-light" href="{cancel_url}">Cancel</a>'),
        ]
        legend_text = "Update a custom form" if self.instance.id else "Create a custom form"
        helper = BaseFormHelper(self)
        helper.layout = cfl.Layout(
            cfl.HTML(f"<legend>{legend_text}</legend>"),
            cfl.Row("name", "description"),
            cfl.Row(
                "schema",
                cfl.Fieldset(
                    "Form Preview", cfl.Div(css_id="schema-preview-frame"), css_class="col-md-6"
                ),
            ),
            "editors",
            "deprecated" if self.instance.id else None,
            cfb.FormActions(*form_actions, css_class="form-actions"),
        )
        return helper


class SchemaPreviewForm(forms.Form):
    """Form for previewing a Dynamic Form schema."""

    schema = forms.JSONField(validators=[PydanticValidator(Schema)])


class ModelBindingForm(forms.ModelForm):

