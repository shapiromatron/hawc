import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestLiteratureAssessmentViewset:
    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="rev@rev.com", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("lit:api:assessment-tags", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-reference-ids", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-reference-tags", args=(db_keys.assessment_working,)),
            reverse(
                "lit:api:assessment-reference-year-histogram", args=(db_keys.assessment_working,)
            ),
            reverse("lit:api:assessment-references-download", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-tag-heatmap", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

        # check permissions for this one; raises an error
        url = reverse("lit:api:assessment-topic-model", args=(db_keys.assessment_working,))
        assert anon_client.get(url).status_code == 403
        with pytest.raises(ValueError):
            assert rev_client.get(url).status_code == 200

    def test_references_download(self, rewrite_data_files: str, db_keys):
        # make sure this export is the format we expect it to be in
        fn = Path(DATA_ROOT / f"api-lit-assessment-references-export.json")
        url = reverse("lit:api:assessment-references-download", args=(db_keys.assessment_final,))
        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2))

        assert len(data) == 4
        assert data == json.loads(fn.read_text())

    def test_tags(self, db_keys):
        url = reverse("lit:api:assessment-tags", kwargs=dict(pk=db_keys.assessment_working))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert len(resp) == 11
        assert resp[0] == {"id": 2, "depth": 2, "name": "Inclusion", "nested_name": "Inclusion"}
        assert resp[-1] == {
            "id": 21,
            "depth": 4,
            "name": "c",
            "nested_name": "Exclusion|Tier III|c",
        }

    def test_reference_ids(self, db_keys):
        url = reverse("lit:api:assessment-reference-ids", kwargs=dict(pk=db_keys.assessment_final))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert resp == [
            {"reference_id": 5, "pubmed_id": 11778423, "hero_id": None},
            {"reference_id": 6, "pubmed_id": 15907334, "hero_id": None},
            {"reference_id": 7, "pubmed_id": 21284075, "hero_id": None},
            {"reference_id": 8, "pubmed_id": 24004895, "hero_id": None},
        ]

    def test_reference_tags(self, db_keys):
        url = reverse("lit:api:assessment-reference-tags", kwargs=dict(pk=db_keys.assessment_final))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert resp == [
            {"reference_id": 5, "tag_id": 12},
            {"reference_id": 6, "tag_id": 13},
            {"reference_id": 7, "tag_id": 13},
            {"reference_id": 8, "tag_id": 12},
        ]

    def test_reference_year_histogram(self, db_keys):
        url = reverse(
            "lit:api:assessment-reference-year-histogram",
            kwargs=dict(pk=db_keys.assessment_working),
        )
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert resp["data"][0]["type"] == "histogram"


@pytest.mark.django_db
class TestReferenceFilterTagViewset:
    def test_references(self):
        # ensure we get a valid json return
        url = reverse("lit:api:tags-references", args=(12,))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert len(resp) == 2
        assert resp[0]["Inclusion"] is True

    def test_references_table_builder(self):
        # ensure we get the expected return
        url = reverse("lit:api:tags-references-table-builder", args=(12,))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert len(resp) == 2
        assert resp[0]["Name"] == "Kawana N, Ishimatsu S, and Kanda K 2001"


@pytest.mark.vcr
@pytest.mark.django_db
class TestSearchViewset:
    def test_success(self, db_keys):
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@team.com", password="pw") is True

        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title",
            "description": "",
            "search_string": "5490558",
        }
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 201

    def test_validation_failures(self, db_keys):
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@team.com", password="pw") is True

        # check that the "GET" method is disabled
        assert c.get(url).status_code == 405

        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title",
            "description": "",
            "search_string": "5490558",
        }

        # check invalid assessment permission
        new_payload = {**payload, **{"assessment": db_keys.assessment_final}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 403
        assert resp.data == {"detail": "Invalid permissions to edit assessment"}

        # check type
        new_payload = {**payload, **{"search_type": "s"}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {"non_field_errors": ["API currently only supports imports"]}

        # check database
        new_payload = {**payload, **{"source": 1}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {"non_field_errors": ["API currently only supports HERO imports"]}

        # check bad csv
        bad_search_strings = [
            "",
            "just a long string of text",
            "not-numeric,but a csv",
            "1a,2b",
            "1,,2",
            "1,2, ,3",
        ]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            resp = c.post(url, new_payload, format="json")
            assert resp.status_code == 400
            assert resp.data == {
                "non_field_errors": [
                    "Must be a comma-separated list of positive integer identifiers"
                ]
            }

        # check bad id lists
        bad_search_strings = ["-1", "123,123"]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            resp = c.post(url, new_payload, format="json")
            assert resp.status_code == 400
            assert resp.data == {
                "non_field_errors": [
                    "At least one positive identifer must exist and must be unique"
                ]
            }

    def test_missing_id_in_hero(self, db_keys):
        """
        This should fail b/c the ID is redirected in HERO (search for HERO ID 41589):
        - https://hero.epa.gov/hero/index.cfm/search
        - https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/5490558

        This is an empty return:
        - https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/41589/recordsperpage/100
        """
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@team.com", password="pw") is True

        # check that the "GET" method is disabled
        assert c.get(url).status_code == 405

        # check success!
        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title 1",
            "description": "",
            "search_string": "41589",
        }
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {
            "non_field_errors": [
                "Import failed; the following HERO IDs could not be imported: 41589"
            ]
        }
