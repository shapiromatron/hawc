import pytest
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_study_detail_api(db_keys):
    client = Client()
    assert client.login(username="team@team.com", password="pw") is True

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
            "name": "working",
        },
        "searches": [],
        "identifiers": [],
        "tags": [],
        "title": "",
        "authors_short": "",
        "authors": "",
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
        "rob_response_values": [27, 26, 25, 22, 24, 20],
    }


@pytest.mark.django_db
def test_study_create_api(db_keys):
    url = "/study/api/study/"
    data = {"reference_id": db_keys.reference_unlinked}

    # reviewers shouldn't be able to edit (create)
    client = APIClient()
    assert client.login(username="rev@rev.com", password="pw") is True
    response = client.post(url, data)
    assert response.status_code == 403

    # public shouldn't be able to edit
    client = APIClient()
    response = client.post(url, data)
    assert response.status_code == 403

    # payload needs to include the required short_citation and full_citation
    client = APIClient()
    assert client.login(username="team@team.com", password="pw") is True
    response = client.post(url, data)
    assert response.status_code == 400
    assert {"short_citation", "full_citation"}.issubset((response.data.keys()))

    # this is a correct request
    data = {
        "reference_id": db_keys.reference_unlinked,
        "short_citation": "Short citation.",
        "full_citation": "Full citation.",
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert data["short_citation"] == response.data["short_citation"]
    assert data["full_citation"] == response.data["full_citation"]

    # references can only be linked to one study
    response = client.post(url, data)
    assert response.status_code == 400
    assert f"Reference ID {db_keys.reference_unlinked} already linked with a study." == str(
        response.data["non_field_errors"][0]
    )
    data["reference_id"] = db_keys.reference_linked
    response = client.post(url, data)
    assert response.status_code == 400
    assert f"Reference ID {db_keys.reference_linked} already linked with a study." == str(
        response.data["non_field_errors"][0]
    )

    # invalid references will not be successful
    data["reference_id"] = "asdf"
    response = client.post(url, data)
    assert response.status_code == 400
    assert "Reference ID does not exist." == str(response.data[0])
