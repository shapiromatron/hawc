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


@pytest.mark.django_db()
def test_study_create_api(db_keys):
    url = lambda reference: f"/study/api/study/?reference_id={reference}"
    unlinked_reference_url = url(db_keys.reference_unlinked)
    linked_reference_url = url(db_keys.reference_linked)
    invalid_reference_url = url("abc")

    # reviewers shouldn't be able to edit (create)
    client = APIClient()
    assert client.login(username="rev@rev.com", password="pw") is True
    response = client.post(unlinked_reference_url)
    assert response.status_code == 403

    # public shouldn't be able to edit
    client = APIClient()
    response = client.post(unlinked_reference_url)
    assert response.status_code == 403

    # payload needs to include the required short_citation and full_citation
    client = APIClient()
    assert client.login(username="team@team.com", password="pw") is True
    response = client.post(unlinked_reference_url)
    assert response.status_code == 400

    # this is a correct request
    data = {"short_citation": "Short citation.", "full_citation": "Full citation."}
    response = client.post(unlinked_reference_url, data)
    assert response.status_code == 200
    # assert set(data).issubset(set(response.data))

    # references can only be linked to one study
    response = client.post(unlinked_reference_url, data)
    assert response.status_code == 200
    response = client.post(linked_reference_url, data)
    assert response.status_code == 200

    # invalid references will not be successful
    response = client.post(invalid_reference_url, data)
    assert response.status_code == 408
