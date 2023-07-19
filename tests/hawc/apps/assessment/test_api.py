import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.assessment import constants


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


@pytest.mark.django_db
class TestAssessmentDetailsAndValues:
    def test_success(self, db_keys):
        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        details_data = {
            "assessment_id": db_keys.assessment_working,
            "project_status": constants.Status.SCOPING,
            "peer_review_status": constants.PeerReviewType.NONE,
        }
        value_data = {
            "assessment_id": db_keys.assessment_working,
            "evaluation_type": constants.EvaluationType.CANCER,
            "value_type": constants.ValueType.OTHER,
            "uncertainty": constants.UncertaintyChoices.ONE,
            "system": "Hepatic",
            "value": 10,
            "value_unit": "mg",
        }
        # only project manager can create Assessment Values or Details
        for url, code, data in [
            (reverse("assessment:api:value-list"), 201, value_data),
            (reverse("assessment:api:details-list"), 201, details_data),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code

    def test_bad_request(self, db_keys):
        client = APIClient()
        details_data = {
            "assessment_id": db_keys.assessment_working,
            "project_status": constants.Status.SCOPING,
            "peer_review_status": constants.PeerReviewType.NONE,
        }
        value_data = {
            "assessment_id": db_keys.assessment_working,
            "evaluation_type": constants.EvaluationType.CANCER,
            "value_type": constants.ValueType.OTHER,
            "uncertainty": constants.UncertaintyChoices.ONE,
            "system": "Hepatic",
            "value": 10,
            "value_unit": "mg",
        }
        # Anon not allowed to use the api
        for url, code, data in [
            (reverse("assessment:api:value-list"), 403, value_data),
            (reverse("assessment:api:details-list"), 403, details_data),
        ]:
            resp = client.post(url, data, format="json")
            assert resp.status_code == code
