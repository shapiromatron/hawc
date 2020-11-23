from pathlib import Path
from textwrap import dedent

from crispy_forms import layout as cfl
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.db import transaction
from django.urls import reverse, reverse_lazy

from hawc.services.epa.dsstox import DssSubstance

from ..common.forms import BaseFormHelper
from ..common.selectable import AutoCompleteSelectMultipleWidget, AutoCompleteWidget
from ..myuser.lookups import HAWCUserLookup
from . import lookups, models


class AssessmentForm(forms.ModelForm):
    class Meta:
        exclude = (
            "enable_literature_review",
            "enable_project_management",
            "enable_data_extraction",
            "enable_risk_of_bias",
            "enable_bmd",
            "enable_summary_text",
        )
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["dtxsids"].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=lookups.DssToxIdLookup
        )
        self.fields["project_manager"].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup
        )
        self.fields["team_members"].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup
        )
        self.fields["reviewers"].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup
        )

    @property
    def helper(self):
        # by default take-up the whole row
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if fld == "dtxsids":
                widget.attrs["class"] = "col-md-10"
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3
                widget.attrs["class"] = widget.attrs.get("class", "") + " html5text"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing HAWC assessment. Fields with * are required.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new assessment",
                "help_text": """
                    Assessments are the fundamental objects in HAWC; all data added to the
                    tool will be related to an assessment. The settings below are used to
                    describe the basic characteristics of the assessment, along with setting
                    up permissions for role-based authorization and access for viewing and
                    editing content associated with an assessment. Fields with * are required.""",
                "cancel_url": reverse_lazy("portal"),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.add_row("name", 3, "col-md-4")
        helper.add_row("cas", 2, "col-md-6")
        helper.add_row("project_manager", 3, "col-md-4")
        helper.add_row("editable", 4, "col-md-3")
        helper.add_row("conflicts_of_interest", 2, "col-md-6")
        helper.add_row("noel_name", 2, "col-md-6")
        helper.add_row("vocabulary", 2, "col-md-6")
        helper.add_create_btn("dtxsids", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        helper.attrs["novalidate"] = ""
        return helper


class AssessmentModulesForm(forms.ModelForm):
    class Meta:
        fields = (
            "enable_literature_review",
            "enable_data_extraction",
            "enable_project_management",
            "enable_risk_of_bias",
            "enable_bmd",
            "enable_summary_text",
        )
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "enable_risk_of_bias"
        ].label = f"Enable {self.instance.get_rob_name_display().lower()}"

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Update enabled modules",
            help_text="""
                HAWC is composed of multiple modules, each designed
                to capture data and decisions related to specific components of a
                health assessment. This screen allows a project-manager to change
                which modules are enabled for this assessment. Modules can be
                enabled or disabled at any time; content already entered into a particular
                module will not be changed when enabling or disabling modules.
                """,
            cancel_url=self.instance.get_absolute_url(),
        )
        return helper


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        exclude = ("content_type", "object_id", "content_object")

    def __init__(self, *args, **kwargs):
        obj = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if obj:
            self.instance.content_type = ContentType.objects.get_for_model(obj)
            self.instance.object_id = obj.id
            self.instance.content_object = obj

    @property
    def helper(self):
        # by default take-up the whole row
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3
                widget.attrs["class"] = widget.attrs.get("class", "") + " html5text"

        if self.instance.id:
            inputs = {"legend_text": f"Update {self.instance}"}
        else:
            inputs = {"legend_text": "Create new attachment"}
        inputs["cancel_url"] = self.instance.get_absolute_url()

        helper = BaseFormHelper(self, **inputs)

        return helper


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create new species",
            help_text="""Create a new species. Note that the creation of a new species is applied as an option for all assessments in HAWC, not just the assessment you're currently working on. Therefore, our staff may periodically review to ensure that the species is indeed new and not pre-existing.""",
            form_actions=[cfl.Submit("save", "Create")],
        )
        helper.add_refresh_page_note()
        return helper

    def clean_name(self):
        return self.cleaned_data["name"].title()


class StrainForm(forms.ModelForm):
    class Meta:
        model = models.Strain
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create a new strain",
            help_text="""Create a new strain. Note that the creation of a new strain is applied as an option for all assessments in HAWC, not just the assessment you're currently working on. Therefore, our staff may periodically review to ensure that the strain is indeed new and not pre-existing.""",
            form_actions=[cfl.Submit("save", "Create")],
        )
        helper.add_refresh_page_note()
        return helper

    def clean_name(self):
        return self.cleaned_data["name"].title()


class DoseUnitsForm(forms.ModelForm):
    class Meta:
        model = models.DoseUnits
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["name"].widget = AutoCompleteWidget(
            lookup_class=lookups.DoseUnitsLookup, allow_new=True
        )

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create new dose/exposure units",
            help_text="""Create a new set of dose/exposure units (for example μg/g). Note that the creation of new dose/exposure-units are all assessments in HAWC, not just the assessment you're currently working on. Therefore, our staff may periodically review to ensure that the dose-units are indeed new and not pre-existing.""",
            form_actions=[cfl.Submit("save", "Create")],
        )
        helper.add_refresh_page_note()
        return helper


class DSSToxForm(forms.ModelForm):
    class Meta:
        model = models.DSSTox
        fields = ("dtxsid",)

    def clean(self):
        data = super().clean()

        try:
            self.substance = DssSubstance.create_from_dtxsid(data.get("dtxsid", ""))
        except ValueError as err:
            self.add_error("dtxsid", str(err))
        return data

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Import new DSSTox substance",
            help_text="""Import a new DSSTox substance by providing the DSSTox substance identifier (DTXSID). You can only import a new substance if it doesn't already exist in HAWC and it returns a valid object from the <a href="https://comptox.epa.gov/dashboard">Chemistry dashboard</a>.""",
            form_actions=[cfl.Submit("save", "Create")],
        )
        helper.add_refresh_page_note()
        return helper

    def save(self, commit=True):
        self.instance.content = self.substance.content
        return super().save(commit=commit)


class EffectTagForm(forms.ModelForm):
    class Meta:
        model = models.EffectTag
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        self.fields["name"].widget = AutoCompleteWidget(
            lookup_class=lookups.EffectTagLookup, allow_new=True
        )

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create new effect tag",
            help_text="""Create a new effect tag. Effect tags are used for describing animal bioassay, epidemiological, or in vitro endpoints. Please take care not to duplicate existing effect tags.""",
            form_actions=[cfl.Submit("save", "Create")],
        )
        helper.add_refresh_page_note()
        return helper


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, disabled=True)
    email = forms.EmailField(disabled=True)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    previous_page = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.back_href = kwargs.pop("back_href")
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["name"].initial = self.user.get_full_name()
        self.fields["email"].initial = self.user.email
        self.fields["previous_page"].initial = self.back_href

    def send_email(self):
        subject = f"[HAWC contact us]: {self.cleaned_data['subject']}"
        body = dedent(
            f"""\
        {self.cleaned_data["message"]}
        ---
        Full name: {self.cleaned_data["name"]}
        Email: {self.cleaned_data["email"]}
        Previous page: {self.cleaned_data["previous_page"]}
        """
        )
        mail_admins(subject, body, fail_silently=False)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Contact HAWC developers",
            help_text="Have a question, comment, or need some help? Use this form to to let us know what's going on.",
            cancel_url=self.back_href,
        )
        helper.form_class = "loginForm"
        return helper


class DatasetForm(forms.ModelForm):
    revision_version = forms.IntegerField(
        disabled=True,
        help_text=models.DatasetRevision._meta.get_field("version").help_text,
        required=False,
    )
    revision_data = forms.FileField(
        label="Dataset", help_text=models.DatasetRevision.data.field.help_text, required=False,
    )
    revision_excel_worksheet_name = forms.CharField(
        max_length=64,
        label="Excel worksheet name",
        help_text=models.DatasetRevision._meta.get_field("excel_worksheet_name").help_text,
        required=False,
    )
    revision_notes = forms.CharField(
        widget=forms.Textarea(),
        label="Dataset version notes",
        help_text=models.DatasetRevision._meta.get_field("notes").help_text,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        if self.instance.id is None:
            self.fields["revision_data"].required = True
        self.fields["revision_version"].initial = self.instance.get_new_version_value()

    @property
    def helper(self):
        # by default take-up the whole row
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3
                widget.attrs["class"] = widget.attrs.get("class", "") + " html5text"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "cancel_url": self.instance.get_absolute_url(),
            }

        else:
            inputs = {
                "legend_text": "Create new dataset",
                "cancel_url": self.instance.assessment.get_absolute_url(),
            }

        inputs[
            "help_text"
        ] = """Datasets are tabular data files that may contain information
        which was captured in external data systems.  A dataset can be used for generating a
        custom visualization. All datasets are public and can be downloaded if an assessment
        is made public. Only team-members or higher can view or download older versions of a
        dataset; the public can only download and see the latest version."""

        helper = BaseFormHelper(self, **inputs)
        helper.add_row("revision_version", 3, ("col-md-2", "col-md-5", "col-md-5 hidden"))
        helper.add_row("revision_notes", 1, ("col-md-12 hidden",))

        return helper

    def clean(self):
        cleaned_data = super().clean()
        revision_data = cleaned_data.get("revision_data")
        revision_excel_worksheet_name = cleaned_data.get("revision_excel_worksheet_name")

        if revision_data is not None:

            valid_extensions = self.instance.VALID_EXTENSIONS

            suffix = Path(revision_data.name).suffix

            if suffix not in valid_extensions:
                self.add_error(
                    "revision_data",
                    f"Invalid file extension: must be one of: {', '.join(sorted(valid_extensions))}",
                )
                return cleaned_data

            df = None
            try:
                df = models.DatasetRevision.try_read_df(
                    revision_data, suffix, revision_excel_worksheet_name,
                )
            except ValueError:
                self.add_error(
                    "revision_data",
                    "Unable to read the submitted dataset file. Please validate that the uploaded file can be read.",
                )

            if df is not None:
                self.revision_df = df
                self.revision_metadata = models.DatasetRevision.Metadata(
                    filename=revision_data.name,
                    extension=suffix,
                    num_rows=df.shape[0],
                    num_columns=df.shape[1],
                    column_names=df.columns.tolist(),
                )

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        """
        Save dataset and create new dataset revision if one was uploaded.
        """
        instance = super().save(commit=commit)
        if self.cleaned_data.get("revision_data"):
            models.DatasetRevision.objects.create(
                dataset=instance,
                version=instance.get_new_version_value(),
                data=self.cleaned_data["revision_data"],
                metadata=self.revision_metadata.dict(),
                excel_worksheet_name=self.cleaned_data["revision_excel_worksheet_name"],
                notes=self.cleaned_data["revision_notes"],
            )
        return instance

    class Meta:
        model = models.Dataset
        fields = ("name", "description", "published")
