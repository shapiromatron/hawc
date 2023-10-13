from crispy_forms import layout as cfl
from django import forms
from django.conf import settings
from django.urls import reverse

from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper, QuillField, check_unique_for_assessment
from . import models
from .actions import RobApproach, clone_approach, load_approach


class RobTextForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasAssessment
        fields = ("help_text",)
        field_classes = {"help_text": QuillField}

    @property
    def helper(self):
        inputs = {
            "cancel_url": reverse("riskofbias:arob_update", args=[self.instance.assessment.pk])
        }

        helper = BaseFormHelper(self, **inputs)
        return helper


class RoBDomainForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasDomain
        fields = (
            "name",
            "is_overall_confidence",
            "description",
        )
        exclude = ("assessment",)
        field_classes = {"description": QuillField}

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment

    @property
    def helper(self):
        inputs = {
            "cancel_url": reverse("riskofbias:arob_update", args=[self.instance.assessment.pk])
        }
        rob_name = self.instance.assessment.get_rob_name_display().lower()
        if self.instance.id:
            inputs["legend_text"] = f"Update {rob_name} domain"
            inputs["help_text"] = "Update an existing domain."
        else:
            inputs["legend_text"] = f"Create new {rob_name} domain"
            inputs["help_text"] = f"Create a new {rob_name} domain."

        helper = BaseFormHelper(self, **inputs)
        helper["description"].wrap(cfl.Field, css_class="col-md-12")
        helper.add_row("name", 2, "col-md-6")
        return helper

    def clean_name(self):
        return check_unique_for_assessment(self, "name")


class RoBMetricForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasMetric
        exclude = ("domain", "hide_description", "sort_order")
        field_classes = {"description": QuillField}

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if domain:
            self.instance.domain = domain
        self.fields["responses"].label = "Judgment choices"

    def clean_key(self):
        key = self.cleaned_data["key"]
        if key:
            qs = models.RiskOfBiasMetric.objects.filter(
                domain__assessment=self.instance.domain.assessment_id,
                key=key,
            )
            if self.instance.id:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise forms.ValidationError("Key is not unique for assessment.")
        return key

    @property
    def helper(self):
        inputs = {
            "cancel_url": reverse(
                "riskofbias:arob_update", args=[self.instance.domain.assessment.pk]
            )
        }
        rob_name = self.instance.domain.assessment.get_rob_name_display().lower()
        if self.instance.id:
            inputs["legend_text"] = f"Update {rob_name} metric"
            inputs["help_text"] = "Update an existing metric."
        else:
            inputs["legend_text"] = f"Create new {rob_name} metric"
            inputs["help_text"] = f"Create a new {rob_name} metric."
        helper = BaseFormHelper(self, **inputs)
        helper.add_row("name", 3, ["col-md-6", "col-md-3", "col-md-3"])
        helper.add_row("description", 2, ["col-md-8", "col-md-4"])
        helper.add_row("required_animal", 3, "col-md-4")
        return helper


class NumberOfReviewersForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasAssessment
        fields = ("number_of_reviewers",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_of_reviewers"].help_text = (
            "The number of independent reviewers required for each study. If "
            "there is more than 1 reviewer, an additional final reviewer will "
            "resolve any conflicts and make a final determination, so there "
            "will be a total of N+1 reviews."
        )

    @property
    def helper(self):
        inputs = {"cancel_url": self.instance.get_absolute_url()}
        helper = BaseFormHelper(self, **inputs)
        return helper


class RiskOfBiasCopyForm(forms.Form):
    assessment = forms.ModelChoiceField(
        label="Select an assessment", queryset=Assessment.objects.all(), empty_label=None
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.user = kwargs.pop("user")
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        self.fields["assessment"].widget.attrs["class"] = "col-md-12"
        self.fields["assessment"].queryset = Assessment.objects.all().user_can_view(
            self.user, exclusion_id=self.assessment.id
        )

    @property
    def helper(self):
        rob_name = self.assessment.get_rob_name_display().lower()
        helper = BaseFormHelper(
            self,
            legend_text=f"Copy {rob_name} approach from another assessment",
            help_text=f"Copy {rob_name} metrics and domains from an existing HAWC assessment which you have access to.",
            cancel_url=reverse("riskofbias:arob_update", args=(self.assessment.id,)),
            submit_text="Copy from assessment",
        )
        helper.layout.insert(3, cfl.Div(css_id="approach"))
        helper.layout.insert(2, cfl.Div(css_id="extra_content_insertion"))
        return helper

    def evaluate(self):
        clone_approach(self.assessment, self.cleaned_data["assessment"], self.user.id)


class RiskOfBiasLoadApproachForm(forms.Form):
    rob_type = forms.TypedChoiceField(
        label="Select an approach",
        choices=RobApproach.choices,
        coerce=int,
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.user = kwargs.pop("user")
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        if settings.HAWC_FLAVOR == "EPA":
            self.fields["rob_type"].initial = RobApproach.EPA_IRIS

    @property
    def helper(self):
        rob_name = self.assessment.get_rob_name_display().lower()
        return BaseFormHelper(
            self,
            legend_text=f"Load a predefined {rob_name} approach",
            help_text="Select a standardized and predefined approach to use in this assessment.",
            cancel_url=reverse("riskofbias:arob_update", args=(self.assessment.id,)),
            submit_text="Load approach",
        )

    def evaluate(self):
        rob_type = RobApproach(self.cleaned_data["rob_type"])
        load_approach(self.assessment.id, rob_type, self.user.id)
