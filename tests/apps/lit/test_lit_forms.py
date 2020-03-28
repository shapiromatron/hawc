import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit import constants
from hawc.apps.lit.forms import ImportForm, RisImportForm
from hawc.apps.lit.models import Reference


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


@pytest.mark.django_db
class TestRisImportForm:
    def test_success(self, db_keys):
        upload_file = open(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"), "rb")
        form = RisImportForm(
            {
                "search_type": "i",
                "source": constants.RIS,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
            },
            {"import_file": SimpleUploadedFile(upload_file.name, upload_file.read())},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid()

        # confirm that after save a reference is
        qs = Reference.objects.filter(authors_short="Ahlborn GJ et al.")
        assert qs.count() == 0
        form.save()
        assert qs.count() == 1

    def test_not_ris_file(self, db_keys):
        form = RisImportForm(
            {
                "search_type": "i",
                "source": constants.RIS,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
            },
            {"import_file": SimpleUploadedFile("test.pdf", b"Nope")},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {"import_file": ['File must have an ".ris" or ".txt" file-extension']}

    def test_unparsable_ris(self, db_keys):
        form = RisImportForm(
            {
                "search_type": "i",
                "source": constants.RIS,
                "title": "demo title",
                "slug": "demo-title",
                "description": "",
            },
            {"import_file": SimpleUploadedFile("test.ris", b"Not valid ris")},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {"import_file": [RisImportForm.UNPARSABLE_RIS]}
