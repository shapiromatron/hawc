from crispy_forms import layout as cfl
from django import forms
from django.forms.widgets import TextInput
from django.urls import reverse

from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper, QuillField, check_unique_for_assessment
from ..lit.constants import ReferenceDatabase
from ..lit.forms import create_external_id, validate_external_id
from ..lit.models import Reference
from ..udf.forms import UDFModelFormMixin
from . import models


class BaseStudyForm(UDFModelFormMixin, forms.ModelForm):
    internal_communications = QuillField(
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
            "eco",
            "coi_reported",
            "coi_details",
            "funding_source",
            "full_text_url",
            "contact_author",
            "ask_author",
            "summary",
            "published",
        )
        field_classes = {"summary": QuillField}

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if type(parent) is Assessment:
            self.instance.assessment = parent
        elif type(parent) is Reference:
            self.instance.assessment = parent.assessment
            self.instance.reference_ptr = parent

        if self.instance:
            self.fields["internal_communications"].initial = self.instance.get_communications()

        self.set_udf_field(self.instance.assessment)
        self.helper = self.setHelper()

    def setHelper(self, inputs: dict | None = None):
        if inputs is None:
            inputs = {}
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"
            else:
                widget.attrs["class"] = "checkbox"

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height(("full_citation", "coi_details", "funding_source", "ask_author"))
        if "authors" in self.fields:
            helper.add_row("authors", 2, "col-md-6")
        helper.add_row("short_citation", 2, "col-md-6")
        helper.add_row("bioassay", 5, ["col-md-3", "col-md-2", "col-md-2", "col-md-3", "col-md-2"])
        helper.add_row("coi_reported", 2, "col-md-6")
        helper.add_row("funding_source", 2, "col-md-6")
        helper.add_row("contact_author", 2, "col-md-6")
        study_type_idx = helper.find_layout_idx_for_field_name("bioassay")
        helper.layout[study_type_idx].css_class = "px-3"
        helper.layout.insert(
            study_type_idx,
            cfl.HTML(
                """<div class="form-row mb-2">
            <p><b>Study Type(s)</b></p>
            <p class="text-muted">Select the type(s) of data contained in this study. Study evaluation and data extraction fields will change depending on the selection. Modifying values after proceeding with study evaluation and/or data extraction may cause data to be removed.</p></div>"""
            ),
        )
        return helper

    def clean_short_citation(self):
        return check_unique_for_assessment(self, "short_citation")

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
            "eco",
            "coi_reported",
            "coi_details",
            "funding_source",
            "full_text_url",
            "contact_author",
            "ask_author",
            "summary",
            "published",
        )
        field_classes = {"summary": QuillField}

    def setHelper(self):
        self.fields["title"].widget = TextInput()
        self.fields["authors"].widget = TextInput()
        self.fields["journal"].widget = TextInput()
        inputs = {
            "legend_text": "Create a new study",
            "help_text": "",
            "cancel_url": reverse("study:list", args=[self.instance.assessment_id]),
        }
        helper = super().setHelper(inputs)
        helper.set_textarea_height(("abstract",))
        return helper


class IdentifierStudyForm(forms.Form):
    db_type = forms.ChoiceField(
        label="Database",
        required=True,
        choices=ReferenceDatabase.import_choices(),
    )
    db_id = forms.CharField(label="Database ID", required=True)

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.assessment = kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        inputs = {
            "legend_text": "Create a new study from identifier",
            "help_text": "Create a new study from a given database and ID.",
            "cancel_url": reverse("study:list", args=[self.assessment.id]),
        }
        self.helper = BaseFormHelper(self, **inputs)
        self.helper.add_row("db_type", 2, ["col-md-4", "col-md-8"])

    def clean_db_type(self):
        return ReferenceDatabase(int(self.cleaned_data["db_type"]))

    def clean(self):
        cleaned_data = super().clean()
        db_type = cleaned_data.get("db_type")
        db_id = cleaned_data.get("db_id")
        if db_type is None or db_id is None:
            return cleaned_data

        # study with this identifier should not already exist
        existing = models.Study.objects.filter(
            assessment_id=self.assessment,
            identifiers__database=db_type,
            identifiers__unique_id=db_id,
        ).first()
        if existing is not None:
            raise forms.ValidationError({"db_id": f"Study already exists; see {existing}"})

        # validate identifier; cache content if it doesn't yet exist
        cleaned_data["identifier"], self._identifier_content = validate_external_id(db_type, db_id)

        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data.copy()
        db_type = cleaned_data.pop("db_type")
        cleaned_data.pop("db_id")

        if (ident := cleaned_data.pop("identifier")) is None:
            ident = create_external_id(db_type, self._identifier_content)

        if (
            ref := Reference.objects.filter(assessment=self.assessment, identifiers=ident).first()
        ) is None:
            ref = ident.create_reference(self.assessment)
            ref.save()
            ref.identifiers.add(ident)

        return models.Study.save_new_from_reference(ref, cleaned_data)


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
