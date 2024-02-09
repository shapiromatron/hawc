from crispy_forms import bootstrap as cfb
from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.urls import reverse, reverse_lazy

from hawc.apps.assessment.autocomplete import AssessmentAutocomplete
from hawc.apps.common.autocomplete.forms import AutocompleteSelectMultipleWidget
from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import BaseFormHelper, PydanticValidator, form_actions_big
from hawc.apps.myuser.autocomplete import UserAutocomplete

from ..assessment.models import Assessment
from ..lit.models import ReferenceFilterTag
from . import constants, models


class UDFForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).model_dump(),
        validators=[PydanticValidator(Schema)],
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            self.instance.creator = user
        self.fields["schema"].label_append_button = {
            "btn_attrs": {
                "hx-indicator": "#spinner",
                "id": "schema-preview-btn",
                "hx-post": reverse_lazy("udf:schema_preview"),
                "hx-target": "#schema-preview-frame",
                "hx-swap": "innerHTML",
                "class": "ml-2 btn btn-primary",
            },
            "btn_content": "Preview",
        }

    class Meta:
        model = models.UserDefinedForm
        fields = (
            "name",
            "description",
            "schema",
            "editors",
            "assessments",
            "published",
            "deprecated",
        )
        widgets = {
            "editors": AutocompleteSelectMultipleWidget(UserAutocomplete),
            "assessments": AutocompleteSelectMultipleWidget(AssessmentAutocomplete),
        }

    @property
    def helper(self):
        self.fields["description"].widget.attrs["rows"] = 8
        legend_text = (
            "Update User Defined Form" if self.instance.id else "Create a User Defined Form"
        )
        helper = BaseFormHelper(self)
        helper.layout = cfl.Layout(
            cfl.Fieldset(
                legend_text,
                cfl.Row(
                    cfl.Column("name", css_class="col-md-6"),
                    cfl.Column(
                        "published",
                        "deprecated" if self.instance.id else None,
                        css_class="col-md-6 align-items-center d-flex",
                    ),
                ),
                cfl.Row(
                    cfl.Column("description", css_class="col-md-6"),
                    cfl.Column("editors", "assessments", css_class="col-md-6"),
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            cfl.Fieldset(
                "Form Schema",
                cfl.Row(
                    cfl.Column("schema"),
                ),
                cfl.Row(
                    cfl.Div(
                        css_id="schema-preview-frame",
                        css_class="bg-lightblue rounded w-100 box-shadow p-4 mx-3 mt-2 mb-4 collapse",
                    )
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            form_actions_big(cancel_url=reverse("udf:udf_list")),
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
        self.fields["form"].queryset = models.UserDefinedForm.objects.all().get_available_udfs(
            user, self.assessment
        )

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
        qs = ReferenceFilterTag.get_assessment_qs(self.instance.assessment_id)
        self.fields["tag"].queryset = qs
        self.fields["tag"].choices = [(el.id, el.get_nested_name()) for el in qs]
        self.fields["form"].queryset = models.UserDefinedForm.objects.all().get_available_udfs(
            user, self.assessment
        )

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
