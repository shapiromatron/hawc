import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestLiteratureAssessmentViewset:
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
        assert resp == [{"reference_id": 2, "pubmed_id": 29641658, "hero_id": None}]

    def test_reference_tags(self, db_keys):
        url = reverse("lit:api:assessment-reference-tags", kwargs=dict(pk=db_keys.assessment_final))
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert resp == [{"reference_id": 2, "tag_id": 13}]

    def test_reference_year_histogram(self, db_keys):
        url = reverse(
            "lit:api:assessment-reference-year-histogram",
            kwargs=dict(pk=db_keys.assessment_working),
        )
        c = APIClient()
        assert c.login(email="pm@pm.com", password="pw") is True
        resp = c.get(url).json()
        assert resp["data"][0]["type"] == "histogram"


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
