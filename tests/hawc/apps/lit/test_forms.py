import re
from pathlib import Path

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import model_to_dict

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit import constants
from hawc.apps.lit.forms import (
    BulkReferenceStudyExtractForm,
    ImportForm,
    LiteratureAssessmentForm,
    ReferenceExcelUploadForm,
    ReferenceForm,
    RisImportForm,
    TagsCopyForm,
)
from hawc.apps.lit.models import Reference, ReferenceFilterTag
from hawc.apps.study.models import Study
from hawc.services.utils.ris import ReferenceParser

from ..test_utils import df_to_form_data


@pytest.mark.django_db
class TestLiteratureAssessmentForm:
    def test_extraction_tag_queryset(self, db_keys):
        instance1 = Assessment.objects.get(id=db_keys.assessment_working).literature_settings
        form1 = LiteratureAssessmentForm(instance=instance1)

        instance2 = Assessment.objects.get(id=db_keys.assessment_final).literature_settings
        form2 = LiteratureAssessmentForm(instance=instance2)

        # ensure that queryset is filtered by assessment and None choice exists
        assert form1.fields["extraction_tag"].choices != form2.fields["extraction_tag"].choices
        assert form1.fields["extraction_tag"].choices[0][0] is None
        assert len(form2.fields["extraction_tag"].choices) == 9

        # ensure we can save `extraction_tag == None`
        data = form1.initial.copy()
        data.update(extraction_tag=None)
        form = LiteratureAssessmentForm(data=data, instance=instance1)
        assert form.is_valid()

        # ensure that a choice from our assessment is valid
        data = form1.initial.copy()
        data.update(extraction_tag=form1.fields["extraction_tag"].choices[-1][0])
        form = LiteratureAssessmentForm(data=data, instance=instance1)
        assert form.is_valid()

        # ensure that a choice from another assessment is invalid
        data = form1.initial.copy()
        data.update(extraction_tag=form2.fields["extraction_tag"].choices[-1][0])
        form = LiteratureAssessmentForm(data=data, instance=instance1)
        assert form.is_valid() is False
        assert (
            form.errors["extraction_tag"][0]
            == "Select a valid choice. That choice is not one of the available choices."
        )


@pytest.mark.vcr
@pytest.mark.django_db
class TestImportForm:
    """
    This test-suite mirrors `tests/apps/lit/test_lit_serializers.TestSearchViewSet`
    """

    def test_success(self, db_keys):
        form = ImportForm(
            {
                "search_type": "i",
                "source": constants.ReferenceDatabase.HERO,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
                "search_string": "5490558, 5490558",
            },
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid()

    def test_validation_failures(self, db_keys):
        parent = Assessment.objects.get(id=db_keys.assessment_working)

        payload = {
            "search_type": "i",
            "source": constants.ReferenceDatabase.HERO,
            "title": "demo title",
            "slug": "demo-title",
            "description": "",
            "search_string": "5490558",
        }

        # check empty
        new_payload = {**payload, **{"search_string": ""}}
        form = ImportForm(new_payload, parent=parent)
        assert not form.is_valid()
        assert form.errors == {"search_string": ["This field is required."]}

        # check bad csv
        bad_search_strings = [
            "just a long string of text",
            "not-numeric,but a csv",
            "1a,2b",
            "1,,2",
            "1,2, ,3",
        ]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            form = ImportForm(new_payload, parent=parent)
            assert not form.is_valid()
            assert form.errors == {
                "search_string": ["Must be a comma-separated list of positive integer identifiers"]
            }

        # check bad id lists
        bad_search_strings = [
            "-1",
        ]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            form = ImportForm(new_payload, parent=parent)
            assert not form.is_valid()
            assert form.errors == {"search_string": ["At least one positive identifier must exist"]}

    def test_missing_id_in_hero(self, db_keys):
        """
        This should fail b/c the ID is redirected in HERO (search for HERO ID 41589):
        - https://hero.epa.gov/hero/index.cfm/search
        - https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/5490558

        This is an empty return:
        - https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/41589/recordsperpage/100
        """

        form = ImportForm(
            {
                "search_type": "i",
                "source": constants.ReferenceDatabase.HERO,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
                "search_string": "41589",
            },
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {
            "search_string": ["The following HERO ID(s) could not be imported: 41589"]
        }


@pytest.mark.vcr
@pytest.mark.django_db
class TestRisImportForm:
    def _create_form(self, db_keys, upload: SimpleUploadedFile) -> RisImportForm:
        # creates a valid input form; use to test RIS file uploads
        return RisImportForm(
            {
                "search_type": "i",
                "source": constants.ReferenceDatabase.RIS,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
            },
            {"import_file": upload},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )

    def test_success(self, db_keys):
        upload_file = Path(__file__).parent / "data/single_ris.txt"

        # check ".txt" file extension
        form = self._create_form(db_keys, SimpleUploadedFile("fn.txt", upload_file.read_bytes()))
        assert form.is_valid()

        # check ".ris" file extension
        form = self._create_form(db_keys, SimpleUploadedFile("fn.ris", upload_file.read_bytes()))
        assert form.is_valid()

        # confirm that after save a reference is
        qs = Reference.objects.filter(authors_short="Ahlborn GJ et al.")
        assert qs.count() == 0
        form.save()
        assert qs.count() == 1

    def test_not_ris_file(self, db_keys):
        form = self._create_form(db_keys, SimpleUploadedFile("test.pdf", b"Nope"))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.RIS_EXTENSION]}

    def test_unparsable_ris(self, db_keys):
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", b"Not valid ris"))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.UNPARSABLE_RIS]}

    def test_doi(self, db_keys):
        base_text = (Path(__file__).parent / "data/single_ris.txt").read_text()
        text = re.sub("DO  - 10.1016/j.fct.2009.02.003", "DO  - " + "a" * 257, base_text)
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", text.encode()))
        assert form.is_valid() is False
        assert "DOI too long" in form.errors["import_file"][0]

    def test_id(self, db_keys):
        base_text = (Path(__file__).parent / "data/single_ris.txt").read_text()
        for replace in ("ID  - abc\n", "ID  - \n", ""):  # non-numeric or missing
            text = re.sub("ID  - 37\r?\n", replace, base_text)
            form = self._create_form(db_keys, SimpleUploadedFile("test.ris", text.encode()))
            assert form.is_valid() is False
            assert form.errors == {"import_file": [ReferenceParser.ID_MISSING]}

    def test_year(self, db_keys):
        base_text = (Path(__file__).parent / "data/single_ris.txt").read_text()
        year_re = "PY  - 2009\r?\n"

        # valid, but cast to None
        for replace in ("PY  - \n", "PY  -   \n", ""):
            text = re.sub(year_re, replace, base_text)
            form = self._create_form(db_keys, SimpleUploadedFile("test.ris", text.encode()))
            assert form.is_valid()
            assert form._references[0]["year"] is None

        # invalid
        for replace in ("PY  - abc\n", "PY  - 2009-2010\n"):
            text = re.sub(year_re, replace, base_text)
            form = self._create_form(db_keys, SimpleUploadedFile("test.ris", text.encode()))
            assert form.is_valid() is False
            assert "Invalid year:" in form.errors["import_file"][0]

    def test_no_references(self, db_keys):
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", b"\n"))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.NO_REFERENCES]}


@pytest.mark.vcr
@pytest.mark.django_db
class TestReferenceForm:
    def test_update_doi(self, db_keys):
        # test updates to reference
        ref = Reference.objects.get(id=5)
        doi = "10.1093/milmed/166.suppl_2.23"
        assert ref.get_doi_id() == doi
        data = {**model_to_dict(ref), "doi_id": doi}

        # bad doi validation check
        form = ReferenceForm(instance=ref, data={**data, "doi_id": "invalid"})
        assert form.is_valid() is False
        assert form.errors["doi_id"][0] == 'Invalid DOI; should be in format "10.1234/s123456"'

        # make sure doi is unchanged by default
        form = ReferenceForm(instance=ref, data=data)
        assert form.fields["doi_id"].initial == doi
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_doi_id() == doi

        # make sure doi is transformed to lowercase
        form = ReferenceForm(instance=ref, data={**data, "doi_id": doi.upper()})
        assert form.fields["doi_id"].initial == doi
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_doi_id() == doi

        # make sure doi can be removed
        form = ReferenceForm(instance=ref, data={**data, "doi_id": None})
        assert form.fields["doi_id"].initial == doi
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_doi_id() is None

        # make sure doi can be added
        form = ReferenceForm(instance=ref, data=data)
        assert form.fields["doi_id"].initial is None
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_doi_id() == doi

        # existing doi validation check
        form = ReferenceForm(instance=Reference.objects.get(id=6), data=data)
        assert form.is_valid() is False
        assert (
            form.errors["doi_id"][0]
            == "Existing HAWC reference with this ID already exists in this assessment: 5"
        )

    def test_update_hero(self, db_keys):
        # test updates to reference
        ref = Reference.objects.get(id=1)
        assert ref.get_hero_id() == 2
        data = {**model_to_dict(ref), "hero_id": 2}

        # existing pubmed validation check
        form = ReferenceForm(instance=ref, data={**data, "hero_id": 3})
        assert form.is_valid() is False
        assert (
            form.errors["hero_id"][0]
            == "Existing HAWC reference with this ID already exists in this assessment: 3"
        )

        # bad pubmed validation check
        form = ReferenceForm(instance=ref, data={**data, "hero_id": -1})
        assert form.is_valid() is False
        assert form.errors["hero_id"][0] == "The following HERO ID(s) could not be imported: -1"

        # make sure pubmed is unchanged by default
        form = ReferenceForm(instance=ref, data=data)
        assert form.fields["hero_id"].initial == 2
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_hero_id() == 2

        # make sure pubmed can be removed
        form = ReferenceForm(instance=ref, data={**data, "hero_id": None})
        assert form.fields["hero_id"].initial == 2
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_hero_id() is None

        # make sure pubmed can be added
        form = ReferenceForm(instance=ref, data={**data, "hero_id": 2})
        assert form.fields["hero_id"].initial is None
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_hero_id() == 2

    def test_update_pubmed(self, db_keys):
        # test updates to reference
        ref = Reference.objects.get(id=5)
        assert ref.get_pubmed_id() == 11778423
        data = {**model_to_dict(ref), "pubmed_id": 11778423}

        # existing pubmed validation check
        form = ReferenceForm(instance=ref, data={**data, "pubmed_id": 15907334})
        assert form.is_valid() is False
        assert (
            form.errors["pubmed_id"][0]
            == "Existing HAWC reference with this ID already exists in this assessment: 6"
        )

        # bad pubmed validation check
        form = ReferenceForm(instance=ref, data={**data, "pubmed_id": -1})
        assert form.is_valid() is False
        assert form.errors["pubmed_id"][0] == "The following PubMed ID(s) could not be imported: -1"

        # make sure pubmed is unchanged by default
        form = ReferenceForm(instance=ref, data=data)
        assert form.fields["pubmed_id"].initial == 11778423
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_pubmed_id() == 11778423

        # make sure pubmed can be removed
        form = ReferenceForm(instance=ref, data={**data, "pubmed_id": None})
        assert form.fields["pubmed_id"].initial == 11778423
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_pubmed_id() is None

        # make sure pubmed can be added
        form = ReferenceForm(instance=ref, data={**data, "pubmed_id": 11778423})
        assert form.fields["pubmed_id"].initial is None
        assert form.is_valid() is True
        form.save()
        ref.refresh_from_db()
        assert ref.get_pubmed_id() == 11778423


@pytest.mark.django_db
class TestBulkReferenceStudyExtractForm:
    def test_success(self, db_keys):
        form = BulkReferenceStudyExtractForm(
            data={
                "references": [Reference.objects.get(pk=db_keys.reference_unlinked)],
                "study_type": ["bioassay", "epi", "epi_meta", "in_vitro"],
            },
            assessment=db_keys.assessment_working,
            reference_qs=Reference.objects.filter(assessment=db_keys.assessment_working),
        )
        assert form.is_valid() is True

        assert (
            Study.objects.filter(
                bioassay=True, epi=True, epi_meta=True, in_vitro=True, title=""
            ).count()
            == 0
        )
        form.save()
        assert (
            Study.objects.filter(
                bioassay=True, epi=True, epi_meta=True, in_vitro=True, title=""
            ).count()
            == 1
        )

    def test_validation_failures(self, db_keys):
        # study has already been created
        form = BulkReferenceStudyExtractForm(
            data={
                "references": [Reference.objects.get(pk=db_keys.reference_linked)],
                "study_type": ["bioassay"],
            },
            assessment=db_keys.assessment_working,
            reference_qs=Reference.objects.filter(assessment=db_keys.assessment_working),
        )
        assert not form.is_valid()
        assert form.errors == {
            "references": [
                f"A Study has already been created from reference #{db_keys.reference_linked}."
            ]
        }

        # reference not in queryset
        form = BulkReferenceStudyExtractForm(
            data={"references": [Reference.objects.get(pk=4)], "study_type": ["bioassay"]},
            assessment=db_keys.assessment_working,
            reference_qs=Reference.objects.filter(assessment=db_keys.assessment_working),
        )
        assert not form.is_valid()
        assert form.errors == {
            "references": ["Select a valid choice. 4 is not one of the available choices."]
        }

        # invalid study type
        form = BulkReferenceStudyExtractForm(
            data={
                "references": [Reference.objects.get(pk=db_keys.reference_unlinked)],
                "study_type": ["crazy"],
            },
            assessment=db_keys.assessment_working,
            reference_qs=Reference.objects.filter(assessment=db_keys.assessment_working),
        )
        assert not form.is_valid()
        assert form.errors == {
            "study_type": ["Select a valid choice. crazy is not one of the available choices."]
        }


@pytest.mark.django_db
class TestTagsCopyForm:
    def test_success(self, pm_user):
        dst_assess = Assessment.objects.get(id=3)
        src_assess = Assessment.objects.get(id=4)
        form = TagsCopyForm(
            assessment=dst_assess,
            data={"assessment": src_assess.id, "confirmation": "confirm"},
            user=pm_user,
        )
        assert not ReferenceFilterTag.get_assessment_qs(3).filter(name="Tier III Demo").exists()
        assert form.is_valid()
        form.copy_tags()
        assert ReferenceFilterTag.get_assessment_qs(3).filter(name="Tier III Demo").exists()


@pytest.mark.django_db
class TestReferenceExcelUploadForm:
    def test_success(self):
        df = pd.DataFrame(
            data={
                "HAWC ID": [1],
                "Full text URL": ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5448372/"],
            }
        )
        form = ReferenceExcelUploadForm(
            instance={},
            assessment=Assessment.objects.get(id=1),
            data={},
            files=df_to_form_data("excel_file", df),
        )
        assert form.is_valid() is True

    def test_validation(self):
        assessment = Assessment.objects.get(id=1)

        # Incorrect file extension
        form = ReferenceExcelUploadForm(
            instance={},
            assessment=assessment,
            data={},
            files={"excel_file": SimpleUploadedFile("z", b"test")},
        )
        assert form.is_valid() is False
        assert "Must be an Excel file with an xlsx extension." in form.errors["excel_file"][0]

        # Incorrect file format
        form = ReferenceExcelUploadForm(
            instance={},
            assessment=assessment,
            data={},
            files={"excel_file": SimpleUploadedFile("test.xlsx", b"test")},
        )
        assert form.is_valid() is False
        assert "Invalid Excel format." in form.errors["excel_file"][0]

        # Incorrect data in Excel
        datasets = [
            # incorrect column names
            ({"test": [1, 2, 3]}, "Invalid Excel format."),
            # non-integer HAWC IDs
            (
                {"HAWC ID": [""], "Full text URL": ["https://www.ncbi.nlm.nih.gov/"]},
                "HAWC IDs must be integers.",
            ),
            # non-URL full text URL
            ({"HAWC ID": [1], "Full text URL": [None]}, "Invalid URLs"),
            ({"HAWC ID": [1], "Full text URL": [""]}, "Invalid URLs"),
            ({"HAWC ID": [1], "Full text URL": ["test"]}, "Invalid URLs"),
        ]
        for data, error_msg in datasets:
            form = ReferenceExcelUploadForm(
                instance={},
                assessment=assessment,
                data={},
                files=df_to_form_data("excel_file", pd.DataFrame(data)),
            )
            assert form.is_valid() is False
            assert error_msg in form.errors["excel_file"][0]
