from django import forms
from django.db.models import Q
from django.forms.widgets import TextInput
from django.urls import reverse

from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper, form_actions_apply_filters
from ..lit.models import Reference
from . import models


class BaseStudyForm(forms.ModelForm):

    internal_communications = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Internal communications regarding this study; this field is only displayed to assessment team members. Could be to describe extraction notes to e.g., reference to full study reports or indicating which outcomes/endpoints in a study were not extracted.",
    )

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

        if self.instance:
            self.fields["internal_communications"].initial = self.instance.get_communications()

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

        for fld in ("summary", "internal_communications"):
            self.fields[fld].widget.attrs["class"] += " html5text"

        if "authors" in self.fields:
            helper.add_row("authors", 2, "col-md-6")
        helper.add_row("short_citation", 2, "col-md-6")
        helper.add_row("bioassay", 4, "col-md-3")
        helper.add_row("coi_reported", 2, "col-md-6")
        helper.add_row("contact_author", 2, "col-md-6")
        return helper

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "internal_communications" in self.changed_data:
            instance.set_communications(self.cleaned_data["internal_communications"])
        return instance


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


class StudyFilterForm(forms.Form):
    name = forms.CharField(required=False, help_text='Study citation text')

    identifier = forms.CharField(required=False, help_text='HERO id, DOI id, etc')

    data_choices = [
        ("bioassay", "Bioassay"),
        ("epi", "Epidemiology"),
        ("epi_meta", "Epidemiology meta-analysis"),
        ("in_vitro", "In vitro"),
    ]
    data_type = forms.ChoiceField(required=False, choices=data_choices, widget=forms.RadioSelect)

    published_choices = [(True, "Published only"), (False, "Unpublished only"), ("", "All studies")]
    published = forms.ChoiceField(
        required=False, choices=published_choices, widget=forms.RadioSelect, initial=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=form_actions_apply_filters())
        helper.form_method = "GET"
        helper.add_row("name", 4, "col-md-3")
        return helper

    def get_query(self):
        query = Q()
        if name := self.cleaned_data.get("name"):
            query &= Q(short_citation__icontains=name)
            query |= Q(full_citation__icontains=name)
        if data_type := self.cleaned_data.get("data_type"):
            query &= Q(**{data_type: True})
        if (published := self.cleaned_data.get("published")) != "":
            query &= Q(published=published)
        if identifier := self.cleaned_data.get("identifier"):
            query &= Q(identifiers__unique_id__icontains=identifier)

        return query
