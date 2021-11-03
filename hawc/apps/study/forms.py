from django import forms
from django.forms.widgets import TextInput
from django.urls import reverse

from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper
from ..lit.models import Reference
from . import models


class BaseStudyForm(forms.ModelForm):
    class Meta:
        model = models.Study
        fields = (
            "short_citation",
            "study_identifier",
            "full_citation",
            "bioassay",
            "in_vitro",
            "epi",
            "epi_meta",
            "coi_reported",
            "coi_details",
            "funding_source",
            "full_text_url",
            "contact_author",
            "ask_author",
            "summary",
            "published",
        )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if type(parent) is Assessment:
            self.instance.assessment = parent
        elif type(parent) is Reference:
            self.instance.reference_ptr = parent

        self.helper = self.setHelper()

    def setHelper(self, inputs={}):
        for fld in ("full_citation", "coi_details", "funding_source", "ask_author"):
            self.fields[fld].widget.attrs["rows"] = 3
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"
            else:
                widget.attrs["class"] = "checkbox"

        helper = BaseFormHelper(self, **inputs)

        if "authors" in self.fields:
            helper.add_row("authors", 2, "col-md-6")
        helper.add_row("short_citation", 2, "col-md-6")
        helper.add_row("bioassay", 4, "col-md-3")
        helper.add_row("coi_reported", 2, "col-md-6")
        helper.add_row("contact_author", 2, "col-md-6")
        return helper


class StudyForm(BaseStudyForm):
    # Study form for updates-only.

    def setHelper(self):
        inputs = {
            "legend_text": "Update an existing study",
            "help_text": "",
            "cancel_url": reverse("study:detail", args=[self.instance.id]),
        }
        return super().setHelper(inputs)


class NewStudyFromReferenceForm(BaseStudyForm):
    # Create new Study from an existing reference.

    def setHelper(self):
        inputs = {
            "legend_text": "Create a new study from an existing reference",
            "help_text": "",
            "cancel_url": reverse(
                "lit:ref_list_extract", args=[self.instance.reference_ptr.assessment.id]
            ),
        }
        return super().setHelper(inputs)


class ReferenceStudyForm(BaseStudyForm):
    # Create both Reference and Study at the same-time.

    class Meta:
        model = models.Study
        fields = (
            "short_citation",
            "study_identifier",
            "full_citation",
            "title",
            "authors",
            "journal",
            "abstract",
            "bioassay",
            "in_vitro",
            "epi",
            "epi_meta",
            "coi_reported",
            "coi_details",
            "funding_source",
            "full_text_url",
            "contact_author",
            "ask_author",
            "summary",
            "published",
        )

    def setHelper(self):
        self.fields["title"].widget = TextInput()
        self.fields["authors"].widget = TextInput()
        self.fields["journal"].widget = TextInput()
        self.fields["abstract"].widget.attrs["rows"] = 3
        inputs = {
            "legend_text": "Create a new study",
            "help_text": "",
            "cancel_url": reverse("study:list", args=[self.instance.assessment_id]),
        }
        return super().setHelper(inputs)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        fields = ("attachment",)

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text="Add an attachment to a study",
            help_text="Upload a file to be associated with his study. Multiple files can be uploaded by creating additional attachments.",
            cancel_url=self.instance.study.get_absolute_url(),
            submit_text="Create attachment",
        )


class StudiesCopy(forms.Form):
    HELP_TEXT = """
    Clone multiple studies and move from one assessment to  another assessment.
    Clones are complete and include most nested data.  Cloned studies do not
    include risk of bias/study evaluation information.
    """

    studies = forms.ModelMultipleChoiceField(
        queryset=models.Study.objects.all(), help_text="Select studies to copy."
    )
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(),
        help_text="Select assessment you wish to copy these studies to.",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        self.fields["assessment"].queryset = self.fields[
            "assessment"
        ].queryset.model.objects.get_editable_assessments(user, assessment.id)
        self.fields["studies"].queryset = self.fields["studies"].queryset.filter(
            assessment_id=assessment.id
        )
        self.helper = self.setHelper(assessment)

    def setHelper(self, assessment):
        self.fields["studies"].widget.attrs["size"] = 15
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs["class"] = "col-md-12"

        inputs = {
            "legend_text": "Copy studies across assessments",
            "help_text": self.HELP_TEXT,
            "cancel_url": reverse("study:list", args=[assessment.id]),
        }

        helper = BaseFormHelper(self, **inputs)

        return helper

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = models.Communication
        exclude = ['content_type', 'object_id']
