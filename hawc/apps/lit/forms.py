import logging
from io import StringIO

import pandas as pd
from django import forms
from django.core.validators import URLValidator
from django.db import transaction
from django.urls import reverse, reverse_lazy

from ...services.utils import ris
from ..assessment.models import Assessment
from ..common.forms import (
    BaseFormHelper,
    ConfirmationField,
    CopyForm,
    QuillField,
    addPopupLink,
    check_unique_for_assessment,
)
from ..study.constants import StudyTypeChoices
from ..study.models import Study
from . import constants, models

logger = logging.getLogger(__name__)


class LiteratureAssessmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = models.ReferenceFilterTag.get_assessment_qs(self.instance.assessment_id)
        self.fields["extraction_tag"].queryset = qs
        self.fields["extraction_tag"].choices = [(el.id, el.get_nested_name()) for el in qs]
        self.fields["extraction_tag"].choices.insert(0, (None, "<none>"))
        self.helper = self.setHelper()

    class Meta:
        model = models.LiteratureAssessment
        fields = (
            "conflict_resolution",
            "extraction_tag",
            "screening_instructions",
            "name_list_1",
            "color_list_1",
            "keyword_list_1",
            "name_list_2",
            "color_list_2",
            "keyword_list_2",
            "name_list_3",
            "color_list_3",
            "keyword_list_3",
        )
        field_classes = {
            "screening_instructions": QuillField,
        }
        widgets = {
            "color_list_1": forms.TextInput(attrs={"type": "color"}),
            "color_list_2": forms.TextInput(attrs={"type": "color"}),
            "color_list_3": forms.TextInput(attrs={"type": "color"}),
        }

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": "Update literature assessment settings",
                "help_text": "Update literature settings for this assessment",
                "cancel_url": reverse_lazy("lit:overview", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
        for fld in ("keyword_list_1", "keyword_list_2", "keyword_list_3"):
            self.fields[fld].widget.attrs["rows"] = 3
        helper.add_row("conflict_resolution", 2, "col-md-6")
        helper.add_row("name_list_1", 3, ["col-md-3 pr-3", "col-md-2 px-2", "col-md-7 pl-3"])
        helper.add_row("name_list_2", 3, ["col-md-3 pr-3", "col-md-2 px-2", "col-md-7 pl-3"])
        helper.add_row("name_list_3", 3, ["col-md-3 pr-3", "col-md-2 px-2", "col-md-7 pl-3"])
        return helper


class SearchForm(forms.ModelForm):
    title_str = "Literature Search"
    help_text = (
        "Create a new literature search. Note that upon creation, "
        "the search will not be executed, but can instead by run on "
        "the next page. The search should be well-tested before "
        "attempting to import into HAWC."
    )

    class Meta:
        model = models.Search
        fields = ("source", "title", "slug", "description", "search_string")
        field_classes = {"description": QuillField, "search_string": QuillField}

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.instance.search_type = "s"
        if assessment:
            self.instance.assessment = assessment

        self.fields["source"].choices = [(1, "PubMed")]  # only current choice
        if "search_string" in self.fields:
            self.fields["search_string"].required = True

    def clean_title(self):
        return check_unique_for_assessment(self, "title")

    def clean_slug(self):
        return check_unique_for_assessment(self, "slug")

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing literature search",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new literature search",
                "help_text": """
                    Create a new literature search. Note that upon creation,
                    the search will not be executed, but can instead by run on
                    the next page. The search should be well-tested before
                    attempting to import into HAWC.""",
                "cancel_url": reverse_lazy("lit:overview", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
        return helper


class ImportForm(SearchForm):
    class Meta(SearchForm.Meta):
        exclude = ("assessment",)
        field_classes = {"description": QuillField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].choices = [(1, "PubMed"), (2, "HERO")]
        self.instance.search_type = "i"
        if self.instance.id is None:
            self.fields[
                "search_string"
            ].help_text = "Enter a comma-separated list of database IDs for import."
            self.fields["search_string"].label = "ID List"
        else:
            self.fields.pop("search_string")
            self.fields.pop("source")

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": """
                    Update an existing literature import. After a literature import
                    has been created, you can no longer edit the source or IDs to import.
                """,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new literature import",
                "help_text": """
                    Import a list of literature from an external database by
                    specifying a comma-separated list of primary keys from the
                    database. This is an import or known references, not a
                    search based on a query.""",
                "cancel_url": reverse_lazy("lit:overview", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    @classmethod
    def validate_import_search_string(cls, search_string) -> list[int]:
        try:
            # convert to a set, then a list to remove duplicate ids
            ids = list(set(int(el) for el in search_string.split(",")))
        except ValueError:
            raise forms.ValidationError(
                "Must be a comma-separated list of positive integer identifiers"
            )

        if len(ids) == 0 or any([el < 0 for el in ids]):
            raise forms.ValidationError("At least one positive identifier must exist")

        return ids

    def clean_search_string(self):
        search_string = self.cleaned_data["search_string"]
        ids = self.validate_import_search_string(search_string)
        source = self.cleaned_data.get("source")
        if source == constants.ReferenceDatabase.HERO:
            content = models.Identifiers.objects.validate_hero_ids(ids)
            self._import_data = dict(ids=ids, content=content)
        elif source == constants.ReferenceDatabase.PUBMED:
            content = models.Identifiers.objects.validate_pubmed_ids(ids)
            self._import_data = dict(ids=ids, content=content)
        else:
            raise forms.ValidationError("Invalid  source")

        return search_string

    @transaction.atomic
    def save(self, commit=True):
        is_create = self.instance.id is None
        search = super().save(commit=commit)
        if is_create:
            search.run_new_import(self._import_data["content"])
        return search


class RisImportForm(SearchForm):
    RIS_EXTENSION = 'File must have an ".ris" or ".txt" file-extension'
    UNPARSABLE_RIS = "File cannot be successfully loaded. Are you sure this is a valid RIS file?  If you are, please contact us and we'll try to fix the issue."
    NO_REFERENCES = "RIS formatted incorrectly; contains 0 references"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].choices = [(3, "RIS (EndNote/Reference Manager)")]
        self.instance.search_type = "i"
        if self.instance.id is None:
            self.fields["import_file"].required = True
            self.fields["import_file"].help_text = """Unicode RIS export file
                ({} for EndNote RIS library preparation)""".format(
                addPopupLink(reverse_lazy("lit:ris_export_instructions"), "view instructions")
            )
        else:
            self.fields.pop("import_file")

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing literature search",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new literature import",
                "help_text": """
                    Import a list of literature from an RIS export; this is a
                    universal data-format which is used by reference management
                    software solutions such as EndNote or Reference Manager.
                """,
                "cancel_url": reverse_lazy("lit:overview", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    class Meta:
        model = models.Search
        fields = ("source", "title", "slug", "description", "import_file")

    def clean_import_file(self):
        fileObj = self.cleaned_data["import_file"]
        if fileObj.size > 1024 * 1024 * 10:
            raise forms.ValidationError("Input file must be <10 MB")

        if fileObj.name[-4:] not in (".txt", ".ris"):
            raise forms.ValidationError(self.RIS_EXTENSION)

        # convert BytesIO file to StringIO file
        with StringIO() as f:
            f.write(fileObj.read().decode("utf-8-sig"))
            f.seek(0)
            fileObj.seek(0)
            readable = ris.RisImporter.file_readable(f)

        if not readable:
            raise forms.ValidationError(self.UNPARSABLE_RIS)

        # now check references
        with StringIO() as f:
            f.write(fileObj.read().decode("utf-8-sig"))
            f.seek(0)
            fileObj.seek(0)
            try:
                self._references = ris.RisImporter(f).references
            except ValueError as err:
                raise forms.ValidationError(str(err))

        # ensure at least one reference exists
        if len(self._references) == 0:
            raise forms.ValidationError(self.NO_REFERENCES)

        return fileObj

    def clean(self):
        """
        In the clean-step, ensure RIS file is valid and references can be
        exported from file before save method. Cache the references on the
        instance method, so that upon import we don't need to re-read file.
        """
        cleaned_data = super().clean()
        if "import_file" in cleaned_data and not self._errors:
            # convert BytesIO file to StringIO file
            with StringIO() as f:
                f.write(cleaned_data["import_file"].read().decode("utf-8-sig"))
                f.seek(0)
                cleaned_data["import_file"].seek(0)
                importer = ris.RisImporter(f)

            self.instance._references = importer.references

    @transaction.atomic
    def save(self, commit=True):
        is_create = self.instance.id is None
        search = super().save(commit=commit)
        if is_create:
            search.run_new_import()
        return search


class SearchCopyForm(CopyForm):
    legend_text = "Copy search or import"
    help_text = """Select an existing search or import from this
        assessment or another assessment and copy it as a template for use in
        this assessment. You will be taken to a new view to create a new
        search, but the form will be pre-populated using values from the
        selected search or import."""
    selector = forms.ModelChoiceField(
        queryset=models.Search.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        self.user = kw.pop("user")
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = models.Search.objects.copyable(self.user).select_related(
            "assessment"
        )
        self.fields["selector"].label_from_instance = (
            lambda obj: f"{obj.assessment} | {{{obj.get_search_type_display()}}} | {obj}"
        )

    def get_success_url(self):
        search = self.cleaned_data["selector"]
        pattern = (
            "lit:search_new"
            if search.search_type == constants.SearchType.SEARCH
            else "lit:import_new"
        )
        url = reverse(pattern, args=(self.parent.pk,))
        return f"{url}?initial={search.pk}"

    def get_cancel_url(self):
        return reverse("lit:overview", args=(self.parent.id,))


def validate_external_id(
    db_type: int, db_id: str | int
) -> tuple[models.Identifiers | None, list | dict | None]:
    """
    Validates an external ID.
    If the identifier already exists it is returned as the first part of a tuple.
    If it does not exist, the content needed to create it is returned as the second part of the tuple.

    Args:
        db_type (int): Database type
        db_id (Union[str, int]): Database ID

    Raises:
        forms.ValidationError: A validation error occurred
        ValueError: An invalid db_type was provided

    Returns:
        tuple[Union[models.Identifiers, None], Union[list, dict, None]]: Existing identifier, content to create identifier
    """
    identifier = models.Identifiers.objects.filter(database=db_type, unique_id=str(db_id)).first()

    if identifier:
        return identifier, None

    if db_type == constants.ReferenceDatabase.PUBMED:
        content = models.Identifiers.objects.validate_pubmed_ids([db_id])
        return None, content
    elif db_type == constants.ReferenceDatabase.HERO:
        content = models.Identifiers.objects.validate_hero_ids([db_id])
        return None, content
    elif db_type == constants.ReferenceDatabase.DOI:
        if not constants.DOI_EXACT.fullmatch(db_id):
            raise forms.ValidationError(
                f'Invalid DOI; should be in format "{constants.DOI_EXAMPLE}"'
            )
        return None, {"database": db_type, "unique_id": str(db_id)}

    else:
        raise ValueError(f"Unknown database type {db_type}.")


def create_external_id(db_type: int, content: list | dict) -> models.Identifiers:
    """
    Creates an identifier with the given content.
    This works in tandem with validate_external_id, using the content returned from that method call.

    Args:
        db_type (int): Database type
        content (Union[list, dict]): Content used to build the identifier with

    Raises:
        ValueError: A content of None was provided
        ValueError: An invalid db_type was provided

    Returns:
        models.Identifiers: Created identifier
    """
    if content is None:
        raise ValueError("Content needed to create external ID")

    if db_type == constants.ReferenceDatabase.PUBMED:
        return models.Identifiers.objects.bulk_create_pubmed_ids(content)[0]
    elif db_type == constants.ReferenceDatabase.HERO:
        return models.Identifiers.objects.bulk_create_hero_ids(content)[0]
    elif db_type == constants.ReferenceDatabase.DOI:
        return models.Identifiers.objects.create(**content)

    else:
        raise ValueError(f"Unknown database type {db_type}.")


class ReferenceForm(forms.ModelForm):
    doi_id = forms.CharField(
        max_length=64,
        label="DOI",
        required=False,
        help_text=f'Add/update DOI. Should be in format: "{constants.DOI_EXAMPLE}"',
    )
    pubmed_id = forms.IntegerField(
        label="PubMed ID", required=False, help_text="Add/update PubMed ID."
    )
    hero_id = forms.IntegerField(label="HERO ID", required=False, help_text="Add/update HERO ID.")

    class Meta:
        model = models.Reference
        fields = (
            "authors_short",
            "title",
            "year",
            "authors",
            "journal",
            "abstract",
            "full_text_url",
            "doi_id",
            "pubmed_id",
            "hero_id",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doi_id"].initial = self.instance.get_doi_id()
        self.fields["pubmed_id"].initial = self.instance.get_pubmed_id()
        self.fields["hero_id"].initial = self.instance.get_hero_id()
        self._ident_additions = []
        self._ident_removals = []

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if fld in ["title", "authors_short", "authors", "journal"]:
                widget.attrs["rows"] = 3

        inputs = {
            "legend_text": "Update reference details",
            "help_text": "Update reference information which was fetched from database or reference upload.",
            "cancel_url": self.instance.get_absolute_url(),
        }

        helper = BaseFormHelper(self, **inputs)

        helper.add_row("authors_short", 3, "col-md-4")
        helper.add_row("authors", 2, "col-md-6")
        helper.add_row("doi_id", 3, "col-md-4")

        return helper

    def _update_identifier(self, db_type: int, field: str):
        value = self.cleaned_data[field]
        if self.fields[field].initial != value:
            if value:
                ident, content = validate_external_id(db_type, value)
                if ident is None:
                    ident = create_external_id(db_type, content)
                else:
                    existing_ref = ident.references.filter(
                        assessment=self.instance.assessment
                    ).first()
                    if existing_ref:
                        raise forms.ValidationError(
                            f"Existing HAWC reference with this ID already exists in this assessment: {existing_ref.id}"
                        )
                self._ident_additions.append(ident)
            existing = self.instance.identifiers.filter(database=db_type)
            self._ident_removals.extend(list(existing))

    def clean_doi_id(self):
        value = self.cleaned_data["doi_id"]
        if value:
            self.cleaned_data["doi_id"] = value.lower()
        self._update_identifier(constants.ReferenceDatabase.DOI, "doi_id")

    def clean_pubmed_id(self):
        self._update_identifier(constants.ReferenceDatabase.PUBMED, "pubmed_id")

    def clean_hero_id(self):
        self._update_identifier(constants.ReferenceDatabase.HERO, "hero_id")

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self._ident_additions:
            instance.identifiers.add(*self._ident_additions)
        if self._ident_removals:
            instance.identifiers.remove(*self._ident_removals)
        return instance


class TagsCopyForm(forms.Form):
    assessment = forms.ModelChoiceField(queryset=Assessment.objects.all(), empty_label=None)
    confirmation = ConfirmationField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.assessment = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.fields["assessment"].widget.attrs["class"] = "col-md-12"
        self.fields["assessment"].queryset = Assessment.objects.all().user_can_view(
            user, exclusion_id=self.assessment.id
        )

    @property
    def helper(self):
        return BaseFormHelper(self)

    def copy_tags(self):
        models.ReferenceFilterTag.copy_tags(self.cleaned_data["assessment"].id, self.assessment.id)


class ReferenceExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        required=True,
        help_text='Upload an Excel file with two columns: a "HAWC ID" column for the HAWC reference ID, and "Full text URL" column which contains a full text URL.',
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        inputs = {
            "legend_text": "Upload full text URLs",
            "help_text": "Using an Excel file, upload full text URLs for multiple references",
            "cancel_url": reverse_lazy("lit:overview", args=[self.assessment.id]),
        }
        helper = BaseFormHelper(self, **inputs)
        return helper

    EXCEL_FORMAT_ERROR = 'Invalid Excel format. The first worksheet in the workbook must contain two columns- "HAWC ID" and "Full text URL", case sensitive.'

    def clean_excel_file(self):
        fn = self.cleaned_data["excel_file"]

        # check extension
        if fn.name[-5:] != ".xlsx":
            raise forms.ValidationError("Must be an Excel file with an xlsx extension.")

        # check parsing
        try:
            df = pd.read_excel(fn.file)
        except Exception as e:
            logger.warning(e)
            raise forms.ValidationError(self.EXCEL_FORMAT_ERROR)

        # check column names
        if df.columns.tolist() != ["HAWC ID", "Full text URL"]:
            raise forms.ValidationError(self.EXCEL_FORMAT_ERROR)

        try:
            hawc_ids = df["HAWC ID"].astype(int).tolist()
        except pd.errors.IntCastingNaNError:
            raise forms.ValidationError("HAWC IDs must be integers.")

        # check valid HAWC IDs
        qs = models.Reference.objects.assessment_qs(self.assessment.id).filter(id__in=hawc_ids)
        if unmatched := (set(hawc_ids) - set(qs.values_list("id", flat=True))):
            raise forms.ValidationError(f"Invalid HAWC IDs: {list(unmatched)}")

        # check valid URLs
        url_errors = []
        validator = URLValidator()
        for _, (id, url) in df.iterrows():
            try:
                validator(url)
            except forms.ValidationError:
                url_errors.append(f"{url} [{id}]")
        if len(url_errors) > 0:
            raise forms.ValidationError(f"Invalid URLs: {', '.join(url_errors)}")

        self.cleaned_data.update(df=df, qs=qs)
        return fn

    def save(self):
        df = self.cleaned_data["df"]
        qs = self.cleaned_data["qs"]
        qs_items = {el.id: el for el in qs}
        updates: list[models.Reference] = []
        for _, (id, url) in df.iterrows():
            ref = qs_items[id]
            ref.full_text_url = url
            updates.append(ref)
        logger.info(
            f"Bulk updated {len(updates)} full text URLs for references in assessment {self.assessment.id}"
        )
        if updates:
            models.Reference.objects.bulk_update(updates, ["full_text_url"])


class BulkReferenceStudyExtractForm(forms.Form):
    references = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, queryset=models.Reference.objects.none(), required=True
    )
    study_type = forms.TypedMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=StudyTypeChoices.choices,
    )

    def clean_references(self):
        data = self.cleaned_data["references"]

        for reference in data:
            if reference.has_study:
                raise forms.ValidationError(
                    f"A Study has already been created from reference #{reference.id}."
                )
        return data

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        self.assessment = kwargs.pop("assessment")
        self.reference_qs = kwargs.pop("reference_qs")
        super().__init__(*args, **kwargs)
        self.fields["references"].queryset = self.reference_qs

    @transaction.atomic
    def save(self):
        references = self.cleaned_data["references"]
        study_type = self.cleaned_data["study_type"]
        for reference in references:
            study_attrs = {st: True for st in study_type}
            Study.save_new_from_reference(reference, study_attrs)


class BulkMergeConflictsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=models.ReferenceFilterTag.objects.all(),
        help_text="Select tag(s) to bulk merge conflicts for. This includes all descendant tag(s).",
    )
    include_without_conflict = forms.BooleanField(
        label="Include references without conflicts",
        help_text="Includes references that are not shown on the conflict resolution page. This refers to references with one unresolved user tag.",
        required=False,
    )
    cache_key = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        tags = models.ReferenceFilterTag.get_assessment_qs(self.assessment.id)
        self.fields["tags"].queryset = tags
        self.fields["tags"].label_from_instance = lambda tag: tag.get_nested_name()
        self.fields["tags"].widget.attrs["size"] = 6

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper
