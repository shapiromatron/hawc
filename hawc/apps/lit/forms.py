import logging
from io import StringIO
from typing import List

import numpy as np
import pandas as pd
from crispy_forms import layout as cfl
from django import forms
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy
from litter_getter import ris

from ..assessment.models import Assessment
from ..common.forms import BaseFormHelper, addPopupLink
from . import constants, models


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
        if "search_string" in self.fields:
            self.fields["search_string"].widget.attrs["rows"] = 5
            self.fields["search_string"].required = True
        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "span12"

        self.helper = self.setHelper()

    def setHelper(self):
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
                "cancel_url": reverse_lazy(
                    "lit:overview", kwargs={"pk": self.instance.assessment.pk}
                ),
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
        else:
            self.fields.pop("search_string")

        self.helper = self.setHelper()

    def setHelper(self):
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
                "cancel_url": reverse_lazy(
                    "lit:overview", kwargs={"pk": self.instance.assessment.pk}
                ),
            }

        helper = BaseFormHelper(self, **inputs)
        return helper

    @classmethod
    def validate_import_search_string(cls, search_string) -> List[int]:
        try:
            ids = [int(el) for el in search_string.split(",")]
        except ValueError:
            raise forms.ValidationError(
                "Must be a comma-separated list of positive integer identifiers"
            )

        if len(ids) == 0 or len(ids) != len(set(ids)) or any([el < 0 for el in ids]):
            raise forms.ValidationError(
                "At least one positive identifer must exist and must be unique"
            )

        return ids

    def clean_search_string(self):
        search_string = self.cleaned_data["search_string"]

        ids = self.validate_import_search_string(search_string)

        if self.cleaned_data["source"] == constants.HERO:
            _, _, content = models.Identifiers.objects.validate_valid_hero_ids(ids)
            self._import_data = dict(ids=ids, content=content)

        return search_string

    @transaction.atomic
    def save(self, commit=True):
        is_create = self.instance.id is None
        search = super().save(commit=commit)
        if is_create:
            if search.source == constants.HERO:
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

    UNPARSABLE_RIS = "File cannot be successfully loaded. Are you sure this is a valid RIS file?  If you are, please contact us and we'll try to fix the issue."

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

        self.helper = self.setHelper()

    def setHelper(self):
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
                "cancel_url": reverse_lazy(
                    "lit:overview", kwargs={"pk": self.instance.assessment.pk}
                ),
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
            raise forms.ValidationError('File must have an ".ris" or ".txt" file-extension')

        try:
            # convert BytesIO file to StringIO file
            with StringIO() as f:
                f.write(fileObj.read().decode("utf-8-sig"))
                f.seek(0)
                fileObj.seek(0)
                readable = ris.RisImporter.file_readable(f)

        except KeyError as err:
            raise forms.ValidationError(
                """
                Invalid key found: {}. Have you followed the instructions below
                for RIS file preparation in Endnote? If you have, please contact
                us and we'll try to fix the issue.""".format(
                    err.message
                )
            )

        if not readable:
            raise forms.ValidationError(self.UNPARSABLE_RIS)

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
        user = kwargs.pop("user", None)
        kwargs.pop("assessment", None)

        super().__init__(*args, **kwargs)

        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs["class"] = "span11"

        assessment_pks = Assessment.objects.get_viewable_assessments(user).values_list(
            "pk", flat=True
        )

        self.fields["searches"].queryset = (
            self.fields["searches"]
            .queryset.filter(assessment__in=assessment_pks)
            .exclude(title="Manual import")
            .order_by("assessment_id")
        )


class ReferenceForm(forms.ModelForm):
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
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if fld in ["title", "authors_short", "authors", "journal"]:
                widget.attrs["rows"] = 3

            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "span12"

        inputs = {
            "legend_text": "Update reference details",
            "help_text": "Update reference information which was fetched from database or reference upload.",  # noqa
            "cancel_url": self.instance.get_absolute_url(),
        }

        helper = BaseFormHelper(self, **inputs)
        # TODO: use new names
        helper.add_fluid_row("authors_short", 3, "span4")
        helper.add_fluid_row("authors", 2, "span6")
        helper.form_class = None
        return helper


class ReferenceFilterTagForm(forms.ModelForm):
    class Meta:
        model = models.ReferenceFilterTag
        fields = "__all__"


class ReferenceSearchForm(forms.Form):
    id = forms.IntegerField(label="HAWC ID", required=False)
    title = forms.CharField(required=False)
    authors = forms.CharField(required=False)
    journal = forms.CharField(label="Journal/year", required=False)
    db_id = forms.IntegerField(
        label="Database unique identifier",
        help_text="Identifiers may include Pubmed ID, DOI, etc.",
        required=False,
    )
    abstract = forms.CharField(label="Abstract", required=False)

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop("assessment_pk", None)
        super().__init__(*args, **kwargs)
        if assessment_pk:
            self.assessment = Assessment.objects.get(pk=assessment_pk)
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = dict(form_actions=[cfl.Submit("search", "Search")],)
        helper = BaseFormHelper(self, **inputs)
        return helper

    def search(self):
        """
        Returns a queryset of reference-search results.
        """
        query = Q(assessment=self.assessment)
        if self.cleaned_data["id"]:
            query &= Q(id=self.cleaned_data["id"])
        if self.cleaned_data["title"]:
            query &= Q(title__icontains=self.cleaned_data["title"])
        if self.cleaned_data["authors"]:
            query &= Q(authors_short__icontains=self.cleaned_data["authors"]) | Q(
                authors__icontains=self.cleaned_data["authors"]
            )
        if self.cleaned_data["journal"]:
            query &= Q(journal__icontains=self.cleaned_data["journal"])
        if self.cleaned_data["db_id"]:
            query &= Q(identifiers__unique_id=self.cleaned_data["db_id"])
        if self.cleaned_data["abstract"]:
            query &= Q(abstract__icontains=self.cleaned_data["abstract"])

        refs = [r.get_json(json_encode=False) for r in models.Reference.objects.filter(query)]

        return refs


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
        self.fields["assessment"].widget.attrs["class"] = "span12"
        self.fields["assessment"].queryset = Assessment.objects.get_viewable_assessments(
            user, exclusion_id=self.assessment.id
        )

    def copy_tags(self):
        models.ReferenceFilterTag.copy_tags(self.assessment, self.cleaned_data["assessment"])


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
        self.helper = self.setHelper()

    def setHelper(self):
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
            df = pd.read_excel(fn.file)
            df = df[["HAWC ID", "Full text URL"]]
            df["Full text URL"].fillna("", inplace=True)
            assert df["HAWC ID"].dtype == np.int64
            assert df["Full text URL"].dtype == np.object0
            self.cleaned_data["df"] = df
        except Exception as e:
            logging.warning(e)
            raise forms.ValidationError(
                "Invalid Excel format. The first worksheet in the workbook "
                'must contain at least two columns- "HAWC ID", and '
                '"Full text URL", case sensitive.'
            )
        return fn
