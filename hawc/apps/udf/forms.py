from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.urls import reverse, reverse_lazy

from ..assessment.models import Assessment
from ..common.autocomplete.forms import AutocompleteSelectMultipleWidget
from ..common.dynamic_forms.schemas import Schema
from ..common.forms import BaseFormHelper, PydanticValidator, form_actions_big
from ..common.helper import get_current_user
from ..common.views import create_object_log
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
                "hx-target": "#schema-preview-fieldset",
                "hx-swap": "innerHTML",
                "class": "ml-2 btn btn-primary",
            },
            "btn_content": "Preview",
        }
        self.fields["schema"].help_text = (
            models.UserDefinedForm.schema.field.help_text
            + "&nbsp;<a id='load-example' href='#'>Load an example</a>."
        )

    def clean_name(self):
        # check unique_together ("creator", "name")
        name = self.cleaned_data.get("name")
        if (
            name != self.instance.name
            and self._meta.model.objects.filter(creator=self.instance.creator, name=name).exists()
        ):
            raise forms.ValidationError("The UDF name must be unique for your account.")
        return name

    @transaction.atomic
    def save(self, commit=True):
        verb = "Created" if self.instance.id is None else "Updated"
        instance = super().save(commit=commit)
        if commit:
            create_object_log(verb, instance, None, self.instance.creator_id, "")
        return instance

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
        legend_text = (
            "Update User Defined Fields (UDF)"
            if self.instance.id
            else "Create a set of User Defined Fields (UDF)"
        )
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("description",), 8)
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
                    cfl.Fieldset(
                        legend="",
                        css_id="schema-preview-fieldset",
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

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "udf" in self.changed_data:
            obj, created = models.ModelUDFContent.objects.update_or_create(
                defaults=dict(content=self.cleaned_data["udf"]),
                model_binding=self.model_binding,
                content_type=self.model_binding.content_type,
                object_id=instance.id,
            )
            create_object_log(
                "",
                obj,
                self.model_binding.assessment_id,
                get_current_user().id,
                f"Updated UDF data for model type {self.model_binding.content_type} on instance {instance.id} (binding {self.model_binding.id}).",
            )
        return instance
