import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.assessment import constants
from hawc.apps.assessment.models import DSSTox

from ..test_utils import get_client


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


@pytest.mark.django_db
class TestDatasetViewSet:
    def test_permissions(self, db_keys):
        client = APIClient()

        # team-member can view anything, including versions and unpublished
        assert client.login(username="team@hawcproject.org", password="pw") is True
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 200),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 200),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_unpublished,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_unpublished,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_unpublished, 1)), 200),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

        # reviewers can only view published final versions
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_unpublished,)), 403),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_unpublished,)), 403),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_unpublished, 1)), 403),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

        # unauthenticated can view public final but not private, versions, or unpublished
        client = APIClient()
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 403),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 403),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_unpublished,)), 403),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_unpublished,)), 403),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_unpublished, 1)), 403),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

    def test_response_data(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # ensure we get expected response
        url = reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)) + "?format=json"
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()[0]["sepal_length"] == 5.1

    def test_response_version(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # ensure we get expected response
        url = (
            reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1))
            + "?format=json"
        )
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()[0]["sepal_length"] == 5.1

        # this version doesn't exist; should get 404
        url = (
            reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 2))
            + "?format=json"
        )
        resp = client.get(url)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestDssToxViewSet:
    def test_expected_response(self):
        dtxsid = "DTXSID6026296"
        client = APIClient()
        url = reverse("assessment:api:dsstox-detail", args=(dtxsid,))
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["dtxsid"] == dtxsid

    @pytest.mark.vcr
    def test_create_dtxsid(self):
        data = {"dtxsid": "DTXSID1020190"}
        client = APIClient()
        url = reverse("assessment:api:dsstox-list")
        resp = client.post(url, data, format="json")
        assert resp.status_code == 201
        created = DSSTox.objects.get(dtxsid=resp.json()["dtxsid"])
        assert (
            resp.json()["content"]["preferredName"] == created.content["preferredName"]
        )

    @pytest.mark.vcr
    def test_existing_dtxsid(self):
        data = {"dtxsid": "DTXSID6026296"}
        client = APIClient()
        url = reverse("assessment:api:dsstox-list")
        resp = client.post(url, data, format="json")
        assert resp.status_code == 400
        assert resp.json()["dtxsid"] == [
            "DSSTox substance with this DSSTox substance identifier (DTXSID) already exists."
        ]


@pytest.mark.django_db
class TestAssessmentDetail:
    def test_success(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        data = {
            "assessment_id": db_keys.assessment_working,
            "project_status": constants.Status.SCOPING,
            "peer_review_status": constants.PeerReviewType.NONE,
        }
        for url, code in [
            (reverse("assessment:api:detail-list"), 201),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code

    def test_bad_request(self, db_keys):
        client = APIClient()
        data = {
            "assessment_id": db_keys.assessment_working,
            "project_status": constants.Status.SCOPING,
            "peer_review_status": constants.PeerReviewType.NONE,
        }
        # Anon not allowed to use the api
        for url, code in [
            (reverse("assessment:api:detail-list"), 403),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code


@pytest.mark.django_db
class TestAssessmentValue:
    def test_success(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        data = {
            "assessment_id": db_keys.assessment_working,
            "evaluation_type": constants.EvaluationType.CANCER,
            "value_type": constants.ValueType.OTHER,
            "uncertainty": constants.UncertaintyChoices.ONE,
            "system": "Hepatic",
            "value": 10,
            "value_unit": "mg",
        }
        # only project manager can create Assessment Values
        for url, code in [
            (reverse("assessment:api:value-list"), 201),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code

    def test_bad_request(self, db_keys):
        client = APIClient()
        data = {
            "assessment_id": db_keys.assessment_working,
            "evaluation_type": constants.EvaluationType.CANCER,
            "value_type": constants.ValueType.OTHER,
            "uncertainty": constants.UncertaintyChoices.ONE,
            "system": "Hepatic",
            "value": 10,
            "value_unit": "mg",
        }
        # Anon not allowed to use the api
        for url, code in [
            (reverse("assessment:api:value-list"), 403),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code


@pytest.mark.django_db
class TestAssessmentViewSet:
    def test_crud(self, db_keys):
        client = APIClient()
        data = {
            "name": "testing",
            "year": "2013",
            "version": "1",
            "assessment_objective": "<p>Test.</p>",
            "authors": "<p>Test.</p>",
            "noel_name": 0,
            "rob_name": 0,
            "editable": "on",
            "creator": 1,
            "project_manager": [2],
            "team_members": [1, 2],
            "reviewers": [1],
            "epi_version": 1,
            "dtxsids_ids": ["DTXSID7020970"],
        }

        # test success
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.post(reverse("assessment:api:assessment-list"), data, format="json")
        assert resp.status_code == 201

        created_id = resp.json()["id"]
        data.update(name="testing1")
        resp = client.patch(reverse("assessment:api:assessment-detail", args=(created_id,)), data)
        assert resp.status_code == 200

        resp = client.delete(reverse("assessment:api:assessment-detail", args=(created_id,)))
        assert resp.status_code == 204

        # test failures
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.post(reverse("assessment:api:assessment-list"), data)
        assert resp.status_code == 403

        resp = client.patch(
            reverse("assessment:api:assessment-detail", args=(db_keys.assessment_working,)), data
        )
        assert resp.status_code == 403

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.delete(
            reverse("assessment:api:assessment-detail", args=(db_keys.assessment_working,))
        )
        assert resp.status_code == 403

    def test_chemical(self):
        url = reverse("assessment:api:assessment-chemical-search")

        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.get(url)
        assert response.status_code == 403

        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        response = client.get(url)
        assert response.status_code == 400
        assert "query" in response.json()

        response = client.get(url + "?query=58-08-2")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestEffectTagViewSet:
    def test_anon_permissions(self):
        anon = get_client(api=True)
        url = reverse("assessment:api:effect-tag-list")

        # list
        response = anon.get(url)
        assert response.status_code == 200

        # create
        response = anon.post(url, {"name": "foo", "slug": "foo"}, format="json")
        assert response.status_code == 403

        # detail
        response = anon.get(reverse("assessment:api:effect-tag-detail", args=(1,)))
        assert response.status_code == 200

    def test_create(self):
        team = get_client("team", api=True)
        url = reverse("assessment:api:effect-tag-list")
        response = team.post(url, {"name": "foo", "slug": "foo"}, format="json")
        assert response.status_code == 201
