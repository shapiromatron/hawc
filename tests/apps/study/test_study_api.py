import pytest
from django.test.client import Client
from django.urls import reverse


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
        "authors": "",
        "year": None,
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
