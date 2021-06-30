import pytest
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.skipif(True, reason="TODO - fix ROB June 2021")
def test_study_detail_api(db_keys):
    client = Client()
    assert client.login(username="team@hawcproject.org", password="pw") is True

    url = reverse("study:api:study-detail", kwargs={"pk": db_keys.study_working})
    response = client.get(url)
    assert response.status_code == 200

    json = response.json()

    # handle this in other tests
    json.pop("riskofbiases")

    assert json == {
        "id": 1,
        "assessment": {
            "id": 1,
            "url": "/assessment/1/",
            "enable_risk_of_bias": True,
            "name": "Chemical Z",
        },
        "searches": [],
        "identifiers": [
            {
                "content": "demo-content",
                "database": "HERO",
                "id": 6,
                "unique_id": "2",
                "url": "http://hero.epa.gov/index.cfm?action=reference.details&reference_id=2",
            }
        ],
        "tags": [],
        "title": "",
        "authors_short": "Frédéric Chopin",
        "authors": "Frédéric Chopin",
        "year": 2010,
        "journal": "",
        "abstract": "",
        "full_text_url": "",
        "created": "2020-01-25T08:23:16.370427-06:00",
        "last_updated": "2020-02-27T14:14:41.479008-06:00",
        "block_id": None,
        "bioassay": True,
        "epi": False,
        "epi_meta": False,
        "in_vitro": False,
        "short_citation": "Foo et al.",
        "full_citation": "Foo et al. 2010",
        "coi_reported": "---",
        "coi_details": "",
        "funding_source": "",
        "study_identifier": "",
        "contact_author": False,
        "ask_author": "",
        "published": False,
        "summary": "",
        "editable": True,
        "url": "/study/1/",
    }


@pytest.mark.django_db
class TestStudyCreateApi:
    def test_permissions(self, db_keys):
        url = reverse("study:api:study-list")
        data = {
            "reference_id": db_keys.reference_unlinked,
            "short_citation": "Short citation.",
            "full_citation": "Full citation.",
        }

        # reviewers shouldn't be able to create
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 403

        # public shouldn't be able to create
        client = APIClient()
        response = client.post(url, data)
        assert response.status_code == 403

    def test_bad_requests(self, db_keys):
        # payload needs to include the required short_citation and full_citation
        url = reverse("study:api:study-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # invalid references will not be successful
        data = {"reference_id": "invalid"}
        response = client.post(url, data)
        assert response.status_code == 400
        assert str(response.data["non_field_errors"][0]) == "Reference ID must be a number."

        # references can only be linked to one study
        data["reference_id"] = db_keys.reference_linked
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data[0])
            == f"Reference ID {db_keys.reference_linked} already linked with a study."
        )

    def test_valid_requests(self, db_keys):
        # this is a correct request
        url = reverse("study:api:study-list")
        data = {
            "reference_id": db_keys.reference_unlinked,
            "short_citation": "Short citation.",
            "full_citation": "Full citation.",
        }
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 201

        assert response.data["short_citation"] == data["short_citation"]
        assert response.data["full_citation"] == data["full_citation"]

        # now that it has been create, we should not be able to create it again
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data[0])
            == f"Reference ID {db_keys.reference_unlinked} already linked with a study."
        )
