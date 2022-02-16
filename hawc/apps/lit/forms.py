import logging
from io import StringIO
from typing import List, Union

import numpy as np
from django import forms
from django.db import transaction
from django.urls import reverse, reverse_lazy

from ...services.utils import ris
from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper, addPopupLink
from ..common.helper import read_excel
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
        fields = ("extraction_tag",)

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": "Update literature assessment settings",
                "help_text": "Update literature settings for this assessment",
                "cancel_url": reverse_lazy("lit:tags_update", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
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

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.instance.search_type = "s"
        if assessment:
            self.instance.assessment = assessment

        self.fields["source"].choices = [(1, "PubMed")]  # only current choice
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["description"].widget.attrs["class"] = "html5text"
        if "search_string" in self.fields:
            self.fields["search_string"].widget.attrs["rows"] = 5
            self.fields["search_string"].required = True
            self.fields["search_string"].widget.attrs["class"] = "html5text"

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].choices = [(1, "PubMed"), (2, "HERO")]
        self.instance.search_type = "i"
        if self.instance.id is None:
            self.fields[
                "search_string"
            ].help_text = "Enter a comma-separated list of database IDs for import."  # noqa
            self.fields["search_string"].label = "ID List"
            self.fields["search_string"].widget.attrs.pop("class")
        else:
            self.fields.pop("search_string")

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
                    Import a list of literature from an external database by
                    specifying a comma-separated list of primary keys from the
                    database. This is an import or known references, not a
                    search based on a query.""",
                "cancel_url": reverse_lazy("lit:overview", args=(self.instance.assessment_id,)),
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    @classmethod
    def validate_import_search_string(cls, search_string) -> List[int]:
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

        if self.cleaned_data["source"] == constants.ReferenceDatabase.HERO:
            _, _, content = models.Identifiers.objects.validate_valid_hero_ids(ids)
            self._import_data = dict(ids=ids, content=content)

        return search_string

    @transaction.atomic
    def save(self, commit=True):
        is_create = self.instance.id is None
        search = super().save(commit=commit)
        if is_create:
            if search.source == constants.ReferenceDatabase.HERO:
                # create missing identifiers from import
                models.Identifiers.objects.bulk_create_hero_ids(self._import_data["content"])
                # get hero identifiers
                identifiers = models.Identifiers.objects.hero(self._import_data["ids"])
                # get or create  reference objects from identifiers
                models.Reference.objects.get_hero_references(search, identifiers)
            else:
                search.run_new_import()
        return search


class RisImportForm(SearchForm):

    RIS_EXTENSION = 'File must have an ".ris" or ".txt" file-extension'
    DOI_TOO_LONG = "DOI field too long on one or more references (length > 256)"
    ID_MISSING = "ID field not found for all references"
    UNPARSABLE_RIS = "File cannot be successfully loaded. Are you sure this is a valid RIS file?  If you are, please contact us and we'll try to fix the issue."
    NO_REFERENCES = "RIS formatted incorrectly; contains 0 references"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].choices = [(3, "RIS (EndNote/Reference Manager)")]
        self.instance.search_type = "i"
        if self.instance.id is None:
            self.fields["import_file"].required = True
            self.fields[
                "import_file"
            ].help_text = """Unicode RIS export file
                ({0} for EndNote RIS library preparation)""".format(
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

        if fileObj.name[-4:] not in (".txt", ".ris",):
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
                references = [ref for ref in ris.RisImporter(f).references]
            except KeyError as err:
                if "id" in err.args:
                    raise forms.ValidationError(self.ID_MISSING)
                else:
                    raise err

        # ensure at least one reference exists
        if len(references) == 0:
            raise forms.ValidationError(self.NO_REFERENCES)

        # ensure the maximum DOI length < 256
        doi_lengths = [len(ref.get("doi", "")) for ref in references if ref.get("doi") is not None]
        if doi_lengths and max(doi_lengths) > 256:
            raise forms.ValidationError(self.DOI_TOO_LONG)

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


class SearchModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.assessment} | {{{obj.get_search_type_display()}}} | {obj}"


class SearchSelectorForm(forms.Form):

    searches = SearchModelChoiceField(queryset=models.Search.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        assessment_pks = Assessment.objects.get_viewable_assessments(self.user).values_list(
            "pk", flat=True
        )

        self.fields["searches"].queryset = (
            self.fields["searches"]
            .queryset.filter(assessment__in=assessment_pks)
            .exclude(title="Manual import")
            .order_by("assessment_id")
        )

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text="Copy search or import",
            help_text="""Select an existing search or import from this
        assessment or another assessment and copy it as a template for use in
        this assessment. You will be taken to a new view to create a new
        search, but the form will be pre-populated using values from the
        selected search or import.""",
            cancel_url=reverse("lit:overview", args=(self.assessment.id,)),
            submit_text="Copy selected as new",
        )


def check_external_id(
    assessment: Assessment, db_type: int, id_: Union[str, int]
) -> models.Identifiers:
    """Validate that the external ID can be used for a reference in this assessment.

    This method has a side effect which may create a new identifier; however this identifier object
    will not be associated with other objects.

    Args:
        assessment (Assessment): Assessment instance
        db_type (int): external reference type
        id_ (int): candidate external ID

    Raises:
        forms.ValidationError: If the external ID cannot be used
        ValueError: If we cannot handle this external ID type

    Returns:
        Identifier: Returns the identifier object which can be used
    """
    identifier = models.Identifiers.objects.filter(database=db_type, unique_id=str(id_)).first()
    if identifier:
        # make sure ID doesn't already exist for this assessment
        existing_reference = identifier.references.filter(assessment=assessment).first()
        if existing_reference:
            raise forms.ValidationError(
                f"Existing HAWC reference with this ID already exists in this assessment: {existing_reference.id}"
            )

    else:
        # try to make an identifier; if it cannot be made an exception is thrown.
        if db_type == constants.ReferenceDatabase.PUBMED:
            identifiers = models.Identifiers.objects.get_pubmed_identifiers([id_])
            if len(identifiers) == 0:
                raise forms.ValidationError(f"Invalid PubMed ID: {id_}")
            identifier = identifiers[0]

        elif db_type == constants.ReferenceDatabase.HERO:
            _, _, content = models.Identifiers.objects.validate_valid_hero_ids([id_])
            models.Identifiers.objects.bulk_create_hero_ids(content)
            identifier = models.Identifiers.objects.get(database=db_type, unique_id=str(id_))

        elif db_type == constants.ReferenceDatabase.DOI:
            if not constants.DOI_EXACT.fullmatch(id_):
                raise forms.ValidationError(
                    f'Invalid DOI; should be in format "{constants.DOI_EXAMPLE}"'
                )
            identifier = models.Identifiers.objects.create(database=db_type, unique_id=str(id_))

        else:
            raise ValueError(f"Unknown database type {db_type}.")

    return identifier


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
            "help_text": "Update reference information which was fetched from database or reference upload.",  # noqa
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
                ident = check_external_id(self.instance.assessment, db_type, value)
                self._ident_additions.append(ident)
            existing = self.instance.identifiers.filter(database=db_type)
            self._ident_removals.extend(list(existing))

    def clean_doi_id(self):
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


class ReferenceFilterTagForm(forms.ModelForm):
    class Meta:
        model = models.ReferenceFilterTag
        fields = "__all__"


class TagReferenceForm(forms.ModelForm):
    class Meta:
        model = models.Reference
        fields = ("tags",)


class TagsCopyForm(forms.Form):

    assessment = forms.ModelChoiceField(queryset=Assessment.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)
        self.fields["assessment"].widget.attrs["class"] = "col-md-12"
        self.fields["assessment"].queryset = Assessment.objects.get_viewable_assessments(
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
        help_text="Upload an Excel file which contains at least two columns: "
        'a "HAWC ID" column for the reference identifier, and a '
        '"Full text URL" column which contains the URL for the '
        "full text.",
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        inputs = {
            "legend_text": "Upload full-text URLs",
            "help_text": "Using an Excel file, upload full-text URLs for multiple references",
            "cancel_url": reverse_lazy("lit:overview", args=[self.assessment.id]),
        }
        helper = BaseFormHelper(self, **inputs)
        return helper

    def clean_excel_file(self):
        fn = self.cleaned_data["excel_file"]
        if fn.name[-5:] not in [".xlsx", ".xlsm"] and fn.name[-4:] not in [".xls"]:
            raise forms.ValidationError(
                "Must be an Excel file with an " "xlsx, xlsm, or xls file extension."
            )

        try:
            df = read_excel(fn.file)
            df = df[["HAWC ID", "Full text URL"]]
            df["Full text URL"].fillna("", inplace=True)
            assert df["HAWC ID"].dtype == np.int64
            assert df["Full text URL"].dtype == np.object0
            self.cleaned_data["df"] = df
        except Exception as e:
            logger.warning(e)
            raise forms.ValidationError(
                "Invalid Excel format. The first worksheet in the workbook "
                'must contain at least two columns- "HAWC ID", and '
                '"Full text URL", case sensitive.'
            )
        return fn


class BulkReferenceStudyExtractForm(forms.Form):
    class Meta:
        model = models.Reference

    reference_ids = forms.CheckboxInput()
    

    def bulk_create_studies(cls, study_type: int, reference_ids: list[int], assessment_id: int):
        """Bulk create studies from a list of reference ids
        Args:
            study_type (int): an integer from 0-4 that maps to the study type the objects will have when created
                0: no study type, 1: bioassay, 2: epi, 3: epi meta, 4: in vitro
            reference_ids (list[int]): the list of reference ids to convert to studies
        """

        for reference_id in reference_ids:
            reference = models.Reference.objects.get(pk=reference_id)

            attrs = {}
            if study_type == 1:
                attrs = {"bioassay": True}

            elif study_type == 2:
                attrs = {"epi": True}

            elif study_type == 3:
                attrs = {"epi_meta": True}

            elif study_type == 4:
                attrs = {"in_vitro": True}

            Study.save_new_from_reference(reference, attrs)

