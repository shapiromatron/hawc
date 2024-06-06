from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.urls import reverse, reverse_lazy

from ..assessment.models import Assessment, Log
from ..common.autocomplete.forms import AutocompleteSelectMultipleWidget
from ..common.dynamic_forms.schemas import Schema
from ..common.forms import BaseFormHelper, PydanticValidator, form_actions_big
from ..lit.models import ReferenceFilterTag
from ..myuser.autocomplete import UserAutocomplete
from . import cache, constants, models


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

        # filter assessment list to a subset of those available
        self.fields["assessments"].queryset = (
            Assessment.objects.all().user_can_view(self.instance.creator).order_by("name")
        )
        self.fields[
            "assessments"
        ].help_text += (
            f" Only assessments the creator ({self.instance.creator}) can view are shown."
        )

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
        self.fields["schema"].help_text = (
            models.UserDefinedForm.schema.field.help_text
            + "&nbsp;<a id='load-example' href='#'>Load an example</a>."
        )

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
        }

    @property
    def helper(self):
        self.fields["description"].widget.attrs["rows"] = 8
        legend_text = (
            "Update User Defined Fields (UDF)"
            if self.instance.id
            else "Create a set of User Defined Fields (UDF)"
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
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("form"),
                cfl.Column(
                    cfl.HTML('<p style="font-size: 1.25rem;">bound to</p>'),
                    css_class="col-md-auto d-flex align-items-center px-4",
                ),
                cfl.Column("content_type"),
            )
        )
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
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("form"),
                cfl.Column(
                    cfl.HTML('<p style="font-size: 1.25rem;">bound to</p>'),
                    css_class="col-md-auto d-flex align-items-center px-4",
                ),
                cfl.Column("tag"),
            )
        )
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
            obj, created = models.ModelUDFContent.objects.update_or_create(
                defaults=dict(content=self.cleaned_data["udf"]),
                model_binding=self.model_binding,
                content_type=self.model_binding.content_type,
                object_id=instance.id,
            )
            Log.objects.create(
                assessment_id=self.instance.get_assessment().id,
                message=f"Updated UDF data for model type {self.model_binding.content_type} on instance {instance.id} (binding {self.model_binding.id}).",
                content_object=obj,
            )
        return instance
