from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import model_to_dict

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit import constants
from hawc.apps.lit.forms import ImportForm, LiteratureAssessmentForm, ReferenceForm, RisImportForm
from hawc.apps.lit.models import Reference


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
        form = LiteratureAssessmentForm(data={"extraction_tag": None}, instance=instance1)
        assert form.is_valid()

        # ensure that a choice from our assessment is valid
        form = LiteratureAssessmentForm(
            data={"extraction_tag": form1.fields["extraction_tag"].choices[-1][0]},
            instance=instance1,
        )
        assert form.is_valid()

        # ensure that a choice from another assessment is invalid
        form = LiteratureAssessmentForm(
            data={"extraction_tag": form2.fields["extraction_tag"].choices[-1][0]},
            instance=instance1,
        )
        assert form.is_valid() is False
        assert (
            form.errors["extraction_tag"][0]
            == "Select a valid choice. That choice is not one of the available choices."
        )


@pytest.mark.vcr
@pytest.mark.django_db
class TestImportForm:
    """
    This test-suite mirrors `tests/apps/lit/test_lit_serializers.TestSearchViewset`
    """

    def test_success(self, db_keys):
        form = ImportForm(
            {
                "search_type": "i",
                "source": constants.HERO,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
                "search_string": "5490558",
            },
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid()

    def test_validation_failures(self, db_keys):
        parent = Assessment.objects.get(id=db_keys.assessment_working)

        payload = {
            "search_type": "i",
            "source": constants.HERO,
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
            "1,1",
        ]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            form = ImportForm(new_payload, parent=parent)
            assert not form.is_valid()
            assert form.errors == {
                "search_string": ["At least one positive identifer must exist and must be unique"]
            }

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
                "source": constants.HERO,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
                "search_string": "41589",
            },
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {
            "search_string": ["Import failed; the following HERO IDs could not be imported: 41589"]
        }


@pytest.mark.vcr
@pytest.mark.django_db
class TestRisImportForm:
    def _create_form(self, db_keys, upload: SimpleUploadedFile) -> RisImportForm:
        # creates a valid input form; use to test RIS file uploads
        return RisImportForm(
            {
                "search_type": "i",
                "source": constants.RIS,
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

    def test_long_doi(self, db_keys):
        fn = Path(__file__).parent / "data/ris-big-doi.txt"
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", fn.read_bytes()))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.DOI_TOO_LONG]}

    def test_missing_doi(self, db_keys):
        fn = Path(__file__).parent / "data/no-id.txt"
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", fn.read_bytes()))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.ID_MISSING]}

    def test_no_references(self, db_keys):
        form = self._create_form(db_keys, SimpleUploadedFile("test.ris", b"\n"))
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.NO_REFERENCES]}


@pytest.mark.vcr
@pytest.mark.django_db
class TestReferenceForm:
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
        assert (
            form.errors["hero_id"][0]
            == "Import failed; the following HERO IDs could not be imported: -1"
        )

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
        assert form.errors["pubmed_id"][0] == "Invalid PubMed ID: -1"

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
