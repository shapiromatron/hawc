from crispy_forms import bootstrap as cfb
from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.urls import reverse, reverse_lazy

from hawc.apps.common.autocomplete.forms import AutocompleteSelectMultipleWidget
from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import BaseFormHelper, PydanticValidator, TextareaButton
from hawc.apps.myuser.autocomplete import UserAutocomplete

from ..assessment.models import Assessment
from . import cache, constants, models


class UDFForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).model_dump(),
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
        model = models.UserDefinedForm
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
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(), disabled=True, widget=forms.HiddenInput
    )
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.annotate(
            full_name=Concat(F("app_label"), Value("."), F("model"))
        ).filter(full_name__in=constants.SUPPORTED_MODELS)
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            # include assessment for unique_together validation
            self.fields["assessment"].initial = self.assessment
            self.instance.assessment = self.assessment
            self.instance.creator = user

    class Meta:
        model = models.ModelBinding
        fields = ("assessment", "content_type", "form")

    @property
    def helper(self):
        cancel_url = (
            self.instance.get_absolute_url()
            if self.instance.id
            else self.instance.assessment.get_udf_list_url()
        )
        legend_text = "Update a model binding" if self.instance.id else "Create a model binding"
        helper = BaseFormHelper(self, legend_text=legend_text, cancel_url=cancel_url)
        return helper


class TagBindingForm(forms.ModelForm):
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(), disabled=True, widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            # include assessment for unique_together validation
            self.fields["assessment"].initial = self.assessment
            self.instance.assessment = self.assessment
            self.instance.creator = user
        qs = models.ReferenceFilterTag.get_assessment_qs(self.instance.assessment_id)
        self.fields["tag"].queryset = qs
        self.fields["tag"].choices = [(el.id, el.get_nested_name()) for el in qs]

    class Meta:
        model = models.TagBinding
        fields = ("assessment", "tag", "form")

    @property
    def helper(self):
        cancel_url = (
            self.instance.get_absolute_url()
            if self.instance.id
            else self.instance.assessment.get_udf_list_url()
        )
        legend_text = "Update a tag binding" if self.instance.id else "Create a tag binding"
        helper = BaseFormHelper(self, legend_text=legend_text, cancel_url=cancel_url)
        return helper


class UDFModelFormMixin:
    """Add UDF to model form."""

    def set_udf_field(self, assessment: Assessment):
        """Set UDF field on model form in a binding exists."""

        self.model_binding = cache.UDFCache.get_model_binding(
            assessment=assessment, Model=self.Meta.model
        )
        if self.model_binding:
            udf_content = models.ModelUDFContent.get_instance(assessment, self.instance)
            initial = udf_content.content if udf_content else None
            udf = self.model_binding.form_field(label="User Defined Fields", initial=initial)
            self.fields["udf"] = udf

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "udf" in self.changed_data:
            models.ModelUDFContent.objects.update_or_create(
                defaults=dict(content=self.cleaned_data["udf"]),
                model_binding=self.model_binding,
                content_type=self.model_binding.content_type,
                object_id=instance.id,
            )
        return instance
