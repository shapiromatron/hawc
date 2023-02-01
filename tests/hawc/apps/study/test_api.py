import pytest
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.study.models import Study

from ..test_utils import check_details_of_last_log_entry


@pytest.mark.django_db
class TestStudyViewset:
    def test_detail(self, db_keys):
        client = Client()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        url = reverse("study:api:study-detail", args=(db_keys.study_working,))
        response = client.get(url)
        assert response.status_code == 200

        json = response.json()

        # handle this in other tests
        json.pop("rob_settings")

        assert len(json.pop("riskofbiases")) == 1
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
            "pubmed_id": None,
            "hero_id": 2,
            "doi": None,
            "created": "2020-01-25T09:23:16.370427-05:00",
            "last_updated": "2020-02-27T15:14:41.479008-05:00",
            "block_id": None,
            "bioassay": True,
            "epi": True,
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

    def test_detail_robs(self, db_keys):
        client = Client()
        url = reverse("study:api:study-rob", args=(db_keys.study_final_bioassay,))

        response = client.get(url)
        assert response.status_code == 403

        assert client.login(username="team@hawcproject.org", password="pw") is True
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(d["active"] is True for d in data)
        assert set(d["final"] for d in data) == {True, False}

    def test_create_permissions(self, db_keys):
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

    def test_create_bad_requests(self, db_keys):
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

    def test_create_valid_requests(self, db_keys):
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
        check_details_of_last_log_entry(response.data["id"], "Created study.study")

        assert response.data["short_citation"] == data["short_citation"]
        assert response.data["full_citation"] == data["full_citation"]

        # now that it has been create, we should not be able to create it again
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data[0])
            == f"Reference ID {db_keys.reference_unlinked} already linked with a study."
        )

    def test_create_from_identifier_permissions(self, db_keys):
        url = reverse("study:api:study-create-from-identifier")
        data = {
            "db_type": "Short citation.",
            "db_id": 1,
            "assessment_id": db_keys.assessment_working,
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

    @pytest.mark.vcr
    def test_create_from_identifier_bad_requests(self, db_keys):
        url = reverse("study:api:study-create-from-identifier")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # payload must have db_type and db_id
        data = {"assessment_id": db_keys.assessment_working}
        response = client.post(url, data)
        assert response.status_code == 400
        assert str(response.data["db_type"][0]) == "This field is required."
        assert str(response.data["db_id"][0]) == "This field is required."

        # study with identifier must not already exist
        existing_study = Study.objects.filter(
            assessment_id=db_keys.assessment_working, identifiers__database=2
        ).first()
        ident = existing_study.identifiers.filter(database=2).first()
        data = {
            "db_type": "HERO",
            "db_id": ident.unique_id,
            "assessment_id": db_keys.assessment_working,
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"db_id": ["Study already exists; see Foo et al. [1]"]}

        # IDs must be valid
        data = {"db_type": "PUBMED", "db_id": -1, "assessment_id": db_keys.assessment_working}
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data["non_field_errors"][0])
            == "The following PubMed ID(s) could not be imported: -1"
        )

    @pytest.mark.vcr
    def test_create_from_identifier_valid_requests(self, db_keys):
        url = reverse("study:api:study-create-from-identifier")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # HERO request
        data = {"db_type": "HERO", "db_id": 2199697, "assessment_id": db_keys.assessment_working}
        response = client.post(url, data)
        assert response.status_code == 201
        assert (
            Study.objects.get(pk=response.data["id"])
            .identifiers.filter(database=2, unique_id=str(2199697))
            .exists()
        )

        # PubMed request with additional fields
        data = {
            "db_type": "PUBMED",
            "db_id": 10357793,
            "assessment_id": db_keys.assessment_working,
            "bioassay": True,
        }
        response = client.post(url, data)
        assert response.status_code == 201
        assert response.data["bioassay"]
        assert (
            Study.objects.get(pk=response.data["id"])
            .identifiers.filter(database=1, unique_id=str(10357793))
            .exists()
        )
