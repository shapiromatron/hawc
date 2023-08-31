from django import forms
from django.urls import reverse, reverse_lazy

from hawc.apps.common.autocomplete.forms import AutocompleteSelectMultipleWidget
from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import BaseFormHelper, PydanticValidator, TextareaButton
from hawc.apps.myuser.autocomplete import UserAutocomplete

from .models import CustomDataExtraction


class CustomDataExtractionForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).dict(),
        validators=[PydanticValidator(Schema)],
        widget=TextareaButton(
            btn_attrs={
                "data-toggle": "modal",
                "data-target": "#schema-preview",
                "hx-post": reverse_lazy("form_library:schema_preview", args=("schema",)),
                "hx-swap": "none",
                "class": "ml-2",
            },
            btn_content="Preview",
            btn_stretch=False,
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["creator"].initial = self.user

    class Meta:
        model = CustomDataExtraction
        exclude = ("parent_form", "created", "last_updated")
        widgets = {
            "editors": AutocompleteSelectMultipleWidget(UserAutocomplete),
            "creator": forms.HiddenInput,
        }

    @property
    def helper(self):
        self.fields["description"].widget.attrs["rows"] = 3
        cancel_url = reverse("portal")  # TODO: replace temp cancel url
        helper = BaseFormHelper(
            self,
            legend_text="Create a custom data extraction form",
            cancel_url=cancel_url,
            submit_text="Create Form",
        )
        return helper


class SchemaPreviewForm(forms.Form):
    """Form for previewing a Dynamic Form schema."""

    schema = forms.JSONField(validators=[PydanticValidator(Schema)])
