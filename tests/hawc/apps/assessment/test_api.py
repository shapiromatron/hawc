import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


@pytest.mark.django_db
class TestDatasetViewset:
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
class TestDssToxViewset:
    def test_expected_response(self):
        dtxsid = "DTXSID6026296"
        client = APIClient()
        url = reverse("assessment:api:dsstox-detail", args=(dtxsid,))
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["dtxsid"] == dtxsid


# TODO - add
# @pytest.mark.django_db
# class TestDownloadPlot:
#     def _get_valid_payload(self, svg_data):
#         return {"output": "svg", "svg": svg_data[0].decode(), "width": 240, "height": 240}

#     def test_invalid(self, svg_data):
#         client = Client()
#         url = reverse("assessment:download_plot")

#         # GET is invalid
#         assert client.get(url).status_code == 405

#         # empty POST is invalid
#         resp = client.post(url, {})
#         assert resp.status_code == 400
#         assert resp.json() == {"valid": False}

#         # incorrect POST is invalid
#         data = self._get_valid_payload(svg_data)
#         data["output"] = "invalid"
#         resp = client.post(url, data)
#         assert resp.status_code == 400
#         assert resp.json() == {"valid": False}

#         # test incorrect svg encoding
#         data = self._get_valid_payload(svg_data)
#         data["svg"] = "💥"
#         resp = client.post(url, data)
#         assert resp.status_code == 400
#         assert resp.json() == {"valid": False}

#     def test_valid(self, svg_data):
#         client = Client()
#         url = reverse("assessment:download_plot")
#         assert client.get(url).status_code == 405
#         resp = client.post(url, self._get_valid_payload(svg_data))
#         assert resp.status_code == 200
