from pathlib import Path
from textwrap import dedent

from crispy_forms import layout as cfl
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.db import transaction
from django.db.models import QuerySet
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from ...services.epa.dsstox import DssSubstance
from ..common.auth.turnstile import Turnstile
from ..common.autocomplete import (
    AutocompleteMultipleChoiceField,
    AutocompleteSelectMultipleWidget,
    AutocompleteTextWidget,
)
from ..common.forms import (
    BaseFormHelper,
    QuillField,
    check_unique_for_assessment,
    form_actions_create_or_close,
)
from ..common.helper import new_window_a
from ..common.widgets import DateCheckboxInput
from ..myuser.autocomplete import UserAutocomplete
from ..study.autocomplete import StudyAutocomplete
from ..vocab.constants import VocabularyNamespace
from . import autocomplete, constants, models


class AssessmentForm(forms.ModelForm):
    internal_communications = QuillField(
        required=False,
        help_text="Internal communications regarding this assessment; this field is only displayed to assessment team members.",
    )

    class Meta:
        fields = (
            "name",
            "year",
            "version",
            "cas",
            "dtxsids",
            "assessment_objective",
            "authors",
            "project_manager",
            "team_members",
            "reviewers",
            "editable",
            "public_on",
            "hide_from_public_page",
            "conflicts_of_interest",
            "funding_source",
        )
        model = models.Assessment
        widgets = {
            "public_on": DateCheckboxInput,
            "dtxsids": AutocompleteSelectMultipleWidget(autocomplete.DSSToxAutocomplete),
            "project_manager": AutocompleteSelectMultipleWidget(UserAutocomplete),
            "team_members": AutocompleteSelectMultipleWidget(UserAutocomplete),
            "reviewers": AutocompleteSelectMultipleWidget(UserAutocomplete),
        }
        field_classes = {
            "assessment_objective": QuillField,
            "authors": QuillField,
            "conflicts_of_interest": QuillField,
            "funding_source": QuillField,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            self.instance.creator = self.user
            self.fields["project_manager"].initial = [self.user]
            self.fields["year"].initial = timezone.now().year

        if not settings.PM_CAN_MAKE_PUBLIC:
            help_text = "&nbsp;<b>Contact the HAWC team to change.</b>"
            for field in ("editable", "public_on", "hide_from_public_page"):
                self.fields[field].disabled = True
                self.fields[field].help_text += help_text

        if self.instance:
            self.fields["internal_communications"].initial = self.instance.get_communications()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "internal_communications" in self.changed_data:
            instance.set_communications(self.cleaned_data["internal_communications"])
        return instance

    @property
    def helper(self):
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
        helper.add_row("assessment_objective", 2, "col-md-6")
        helper.add_row("project_manager", 3, "col-md-4")
        helper.add_row("editable", 3, "col-md-4")
        helper.add_row("conflicts_of_interest", 2, "col-md-6")
        helper.add_create_btn("dtxsids", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        helper.attrs["novalidate"] = ""
        return helper


class AssessmentDetailForm(forms.ModelForm):
    LEGEND = "Additional Assessment Details"
    HELP_TEXT = "Add additional details for this assessment."

    assessment = forms.Field(disabled=True, widget=forms.HiddenInput)

    class Meta:
        model = models.AssessmentDetail
        fields = "__all__"
        widgets = {
            "project_type": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentDetailAutocomplete, field="project_type"
            ),
        }

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if self.assessment:
            self.fields["assessment"].initial = self.assessment
            self.instance.assessment = self.assessment

    def clean(self) -> dict:
        cleaned_data = super().clean()
        # set None to an empty dict; see https://code.djangoproject.com/ticket/27697
        if cleaned_data.get("extra") is None:
            cleaned_data["extra"] = dict()
        return cleaned_data

    @property
    def helper(self):
        cancel_url = (
            self.instance.get_absolute_url()
            if self.instance.id
            else self.instance.assessment.get_absolute_url()
        )
        helper = BaseFormHelper(
            self, legend_text=self.LEGEND, help_text=self.HELP_TEXT, cancel_url=cancel_url
        )
        helper.set_textarea_height(("extra",), 3)
        helper.add_row("project_type", 3, "col-md-4")
        helper.add_row("peer_review_status", 3, "col-md-4")
        helper.add_row("report_id", 3, "col-md-4")
        return helper


class AssessmentValueForm(forms.ModelForm):
    CREATE_LEGEND = "Create Assessment Value"
    UPDATE_LEGEND = "Update Assessment Value"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update current assessment value."

    studies = AutocompleteMultipleChoiceField(
        autocomplete_class=StudyAutocomplete,
        help_text=models.AssessmentValue.studies.field.help_text,
        required=False,
    )

    class Meta:
        model = models.AssessmentValue
        exclude = ["assessment"]
        widgets = {
            "system": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="system"
            ),
            "species_studied": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="species_studied"
            ),
            "duration": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="duration"
            ),
            "tumor_type": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="tumor_type"
            ),
            "extrapolation_method": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete,
                field="extrapolation_method",
            ),
            "evidence": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="evidence"
            ),
            "value_type_qualifier": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete,
                field="value_type_qualifier",
            ),
            "value_unit": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="value_unit"
            ),
            "pod_unit": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="pod_unit"
            ),
            "pod_type": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="pod_type"
            ),
            "confidence": AutocompleteTextWidget(
                autocomplete_class=autocomplete.AssessmentValueAutocomplete, field="confidence"
            ),
        }

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        self.fields["studies"].set_filters({"assessment_id": self.instance.assessment.id})

    def clean(self):
        cleaned_data = super().clean()

        # set None to an empty dict; see https://code.djangoproject.com/ticket/27697
        if cleaned_data.get("extra") is None:
            cleaned_data["extra"] = dict()

        evaluation_type = cleaned_data.get("evaluation_type")
        if evaluation_type != constants.EvaluationType.NONCANCER:
            for field in ["tumor_type", "extrapolation_method", "evidence"]:
                if not cleaned_data.get(field):
                    msg = "Required for Cancer evaluation types."
                    self.add_error(field, msg)
        if evaluation_type != constants.EvaluationType.CANCER:
            if not cleaned_data.get("uncertainty"):
                msg = "Required for Noncancer evaluation types."
                self.add_error("uncertainty", msg)

    @property
    def helper(self):
        if self.instance.id:
            helper = BaseFormHelper(
                self,
                help_text=self.UPDATE_HELP_TEXT,
                legend_text=self.UPDATE_LEGEND,
                cancel_url=self.instance.get_absolute_url(),
            )

        else:
            helper = BaseFormHelper(
                self,
                legend_text=self.CREATE_LEGEND,
                help_text=self.CREATE_HELP_TEXT,
                cancel_url=self.instance.assessment.get_absolute_url(),
            )

        helper.set_textarea_height(("comments", "basis", "extra"), 3)
        helper.add_row("evaluation_type", 2, "col-md-6")
        helper.add_row(
            "value_type", 5, ["col-md-3", "col-md-3", "col-md-2", "col-md-2", "col-md-2"]
        )
        helper.add_row("confidence", 3, "col-md-4")
        helper.add_row("pod_type", 4, "col-md-3")
        helper.add_row("species_studied", 3, "col-md-4")
        helper.add_row("tumor_type", 2, "col-md-6")
        helper.add_row("comments", 2, "col-md-6")

        return helper


class AssessmentAdminForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Assessment
        widgets = {
            "dtxsids": AutocompleteSelectMultiple(
                models.Assessment._meta.get_field("dtxsids"), admin.site
            ),
            "project_manager": AutocompleteSelectMultiple(
                models.Assessment._meta.get_field("project_manager"), admin.site
            ),
            "team_members": AutocompleteSelectMultiple(
                models.Assessment._meta.get_field("team_members"), admin.site
            ),
            "reviewers": AutocompleteSelectMultiple(
                models.Assessment._meta.get_field("reviewers"), admin.site
            ),
        }


class AssessmentModulesForm(forms.ModelForm):
    class Meta:
        fields = (
            "enable_literature_review",
            "enable_data_extraction",
            "enable_project_management",
            "enable_risk_of_bias",
            "enable_bmd",
            "enable_summary_tables",
            "enable_visuals",
            "enable_downloads",
            "noel_name",
            "rob_name",
            "vocabulary",
            "epi_version",
        )
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "enable_risk_of_bias"
        ].label = f"Enable {self.instance.get_rob_name_display().lower()}"
        self.fields["vocabulary"].choices = VocabularyNamespace.display_choices()

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Update modules",
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
        helper.add_row("enable_literature_review", 3, "col-lg-4")
        helper.add_row("enable_risk_of_bias", 3, "col-lg-4")
        helper.add_row("enable_visuals", 2, "col-lg-6")
        helper.add_row("noel_name", 3, "col-lg-4")
        helper.add_row("epi_version", 1, "col-lg-4")
        return helper


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        exclude = ("content_type", "object_id", "content_object")
        field_classes = {"description": QuillField}

    def __init__(self, *args, **kwargs):
        obj = kwargs.pop("parent", None)
        prefix = f"attachment-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if obj:
            self.instance.content_type = ContentType.objects.get_for_model(obj)
            self.instance.object_id = obj.id
            self.instance.content_object = obj

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("title", 2, "col-md-6")
        helper.add_row("publicly_available", 2, "col-md-6")
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
            form_actions=form_actions_create_or_close(),
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
            form_actions=form_actions_create_or_close(),
        )
        helper.add_refresh_page_note()
        return helper

    def clean_name(self):
        return self.cleaned_data["name"].title()


class DoseUnitsForm(forms.ModelForm):
    class Meta:
        model = models.DoseUnits
        fields = "__all__"
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.DoseUnitsAutocomplete, field="name"
            )
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create new dose/exposure units",
            help_text="""Create a new set of dose/exposure units (for example μg/g). Note that the creation of new dose/exposure-units are all assessments in HAWC, not just the assessment you're currently working on. Therefore, our staff may periodically review to ensure that the dose-units are indeed new and not pre-existing.""",
            form_actions=form_actions_create_or_close(),
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
            help_text=f"""Import a new DSSTox substance by providing the DSSTox substance identifier (DTXSID). You can only import a new substance if it doesn't already exist in HAWC and it returns a valid object from the {new_window_a('https://comptox.epa.gov/dashboard', 'Chemistry dashboard')}.""",
            form_actions=form_actions_create_or_close(),
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
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.EffectTagAutocomplete, field="name"
            )
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Create new effect tag",
            help_text="""Create a new effect tag. Effect tags are used for describing animal bioassay, epidemiological, or in vitro endpoints. Please take care not to duplicate existing effect tags.""",
            form_actions=form_actions_create_or_close(),
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
        if self.user.is_anonymous:
            self.fields["name"].disabled = False
            self.fields["email"].disabled = False
        else:
            self.fields["name"].initial = self.user.get_full_name()
            self.fields["email"].initial = self.user.email
        self.enable_turnstile: bool = self.user.is_anonymous
        if self.enable_turnstile:
            self.turnstile = Turnstile()
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
            legend_text="Contact us",
            help_text="Have a question, comment, or need some help? Use this form to to let us know what's going on.",
            cancel_url=self.back_href,
        )
        if self.enable_turnstile:
            helper.layout.insert(len(helper.layout) - 1, self.turnstile.render())
        return helper

    def clean(self):
        if self.enable_turnstile:
            self.turnstile.validate(self.data)
        return self.cleaned_data


class SearchForm(forms.Form):
    all_public = forms.BooleanField(required=False, initial=True)
    public = forms.ModelMultipleChoiceField(
        queryset=models.Assessment.objects.all(), required=False
    )
    all_internal = forms.BooleanField(required=False, initial=True)
    internal = forms.ModelMultipleChoiceField(
        queryset=models.Assessment.objects.all(), required=False
    )
    type = forms.ChoiceField(required=True, choices=(("visual", "Visuals"), ("study", "Studies")))
    query = forms.CharField(max_length=128, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["public"].queryset = self.fields["public"].queryset.public().order_by("name")
        if self.user.is_anonymous:
            self.fields.pop("all_internal")
            self.fields.pop("internal")
        else:
            self.fields["internal"].queryset = (
                self.fields["internal"].queryset.user_can_view(self.user).order_by("name")
            )

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_method = "GET"

        internal_fields = tuple() if self.user.is_anonymous else ("all_internal", "internal")

        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("all_public", "public"),
                cfl.Column(*internal_fields),
            ),
            cfl.Row(
                cfl.Column("query", css_class="col-6"),
                cfl.Column("type", css_class="col-4"),
                cfl.Column(
                    cfl.Submit("search", "Search", css_class="btn-block py-4"), css_class="col-2"
                ),
            ),
        )
        return helper

    def search(self):
        from itertools import chain

        from django.db.models import Q

        from ..summary.models import Visual

        data = self.cleaned_data
        assessment_filters = Q(
            id__in=[a.id for a in chain(data.get("public", []), data.get("internal", []))]
        )
        if data["all_public"]:
            assessment_filters |= Q(public_on__isnull=False, hide_from_public_page=False)
        if data["all_internal"]:
            assessment_filters |= (
                Q(project_manager=self.user) | Q(team_members=self.user) | Q(reviewers=self.user)
            )

        assessment_ids = list(
            models.Assessment.objects.filter(assessment_filters).values_list("id", flat=True)
        )
        # search public, published visuals and data pivots
        # search internal, published and unpublished visuals and data pivots
        # TODO - search by tags
        # TODO - search studies

        filters = Q()
        if query := data.get("query"):
            filters &= Q(title__icontains=query) | Q(labels__name__icontains=query)
        return (
            Visual.objects.filter(assessment__in=assessment_ids)
            .filter(filters)
            .select_related("assessment")
            .prefetch_related("labels")[:100]
        )


class DatasetForm(forms.ModelForm):
    revision_version = forms.IntegerField(
        disabled=True,
        help_text=models.DatasetRevision._meta.get_field("version").help_text,
        required=False,
    )
    revision_data = forms.FileField(
        label="Dataset",
        help_text=models.DatasetRevision.data.field.help_text,
        required=False,
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

        inputs["help_text"] = """Datasets are tabular data files that may contain information
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
                    revision_data,
                    suffix,
                    revision_excel_worksheet_name,
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

    def clean_name(self):
        return check_unique_for_assessment(self, "name")

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
                metadata=self.revision_metadata.model_dump(),
                excel_worksheet_name=self.cleaned_data["revision_excel_worksheet_name"],
                notes=self.cleaned_data["revision_notes"],
            )
        return instance

    class Meta:
        model = models.Dataset
        fields = ("name", "description", "published")
        field_classes = {"description": QuillField}


class LabelForm(forms.ModelForm):
    parent = forms.ModelChoiceField(None, empty_label=None)

    after = forms.ModelChoiceField(
        None,
        required=False,
        empty_label="--- last ---",
        initial=None,
        help_text="Move label after a sibling label.",
    )

    class Meta:
        model = models.Label
        fields = ["name", "description", "parent", "color", "published"]

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("assessment", None)
        prefix = f"label-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        if self.instance.pk is not None:
            self.fields["parent"].initial = self.instance.get_parent()
        tree_queryset, root = self.get_tree_queryset()
        self.fields["parent"].queryset = tree_queryset
        self.fields["after"].queryset = tree_queryset.exclude(id=root.pk)
        self.fields["parent"].label_from_instance = lambda label: label.get_nested_name()
        self.fields["after"].label_from_instance = lambda label: label.get_nested_name()
        self.fields["after"].hover_help = True
        self.fields["description"].widget.attrs["rows"] = 2

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("name", "published", css_class="col-md-2"),
                cfl.Column("color", css_class="col-md-1"),
                cfl.Column("description", css_class="col"),
                cfl.Column("parent", css_class="col-md-2"),
                cfl.Column("after", css_class="col-md-2"),
            ),
        )
        return helper

    def get_tree_queryset(self) -> tuple[QuerySet[models.Label], models.Label]:
        root = models.Label.get_assessment_root(self.instance.assessment.pk)
        queryset = models.Label.get_tree(root)
        if self.instance.pk is not None:
            queryset = queryset.exclude(
                path__startswith=self.instance.path, depth__gte=self.instance.depth
            )
        return queryset, root

    def clean(self):
        cleaned_data = super().clean()
        parent_conflict_msg = "Cannot be published: parent label is unpublished."
        descendant_conflict_msg = "Cannot be unpublished: child label is published."
        after_conflict_msg = "Must be a child of the 'parent' label."
        #  check that 'after' and parent align
        if "after" in self.changed_data:
            if not self.cleaned_data["after"].is_child_of(self.cleaned_data["parent"]):
                self.add_error("after", after_conflict_msg)
        # if published changed, check parent and subtree published status
        if "published" in self.changed_data:
            if cleaned_data["published"] and not cleaned_data["parent"].published:
                self.add_error("published", parent_conflict_msg)
            elif not cleaned_data["published"] and self.instance.pk is not None:
                descendants = self.instance.get_descendants()
                if any(_.published for _ in descendants):
                    self.add_error("published", descendant_conflict_msg)
        # else if parent changed, check parent published status
        elif "parent" in self.changed_data:
            if cleaned_data["published"] and not cleaned_data["parent"].published:
                self.add_error("parent", parent_conflict_msg)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            parent = self.cleaned_data["parent"]
            after = self.cleaned_data["after"]
            # handle new instance
            if instance.pk is None:
                instance = models.Label.create_tag(
                    assessment_id=instance.assessment.pk, parent_id=parent.pk, instance=instance
                )
                if "after" in self.changed_data:
                    instance.move(after, pos="right")
            # handle existing instance
            else:
                instance.save()
                if "after" in self.changed_data:
                    instance.move(after, pos="right")
                elif "parent" in self.changed_data:
                    instance.move(parent, pos="last-child")
            self.save_m2m()
        return instance


class LabelItemForm(forms.Form):
    labels = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Label.objects.all(),
        label="Labels",
        help_text="Select label(s) to apply.",
    )

    def __init__(self, *args, **kwargs):
        content_object = kwargs.pop("content_object", None)
        self.content_type = kwargs.pop("content_type")
        self.object_id = kwargs.pop("object_id")
        super().__init__(*args, **kwargs)
        labels = models.Label.get_assessment_qs(content_object.get_assessment().pk)
        self.fields["labels"].queryset = labels
        self.fields["labels"].label_from_instance = lambda label: label.get_nested_name()

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper

    @transaction.atomic
    def save(self):
        qs = models.LabeledItem.objects.filter(
            content_type_id=self.content_type, object_id=self.object_id
        )
        existing = set(qs.values_list("label_id", flat=True))
        next = set(label.id for label in self.cleaned_data["labels"])

        deletes = existing - next
        if deletes:
            qs.filter(label_id__in=deletes).delete()

        creates = next - existing
        if creates:
            labels = [
                models.LabeledItem(
                    label_id=label_id, content_type_id=self.content_type, object_id=self.object_id
                )
                for label_id in creates
            ]
            models.LabeledItem.objects.bulk_create(labels)
