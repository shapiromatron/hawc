import time

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.vcr
class TestCasrnView:
    def test_happy_path(self):
        casrn = "7732-18-5"
        url = reverse("assessment:casrn_detail", args=(casrn,))

        assert url == "/assessment/casrn/7732-18-5/"

        # first time, acknowledge request
        client = APIClient()
        resp = client.get(url)
        data = resp.json()
        assert data == {"status": "requesting"}

        # wait until success
        waited_for = 0
        while waited_for < 10:
            resp = client.get(url)
            data = resp.json()
            if data["status"] == "success":
                break

            time.sleep(1)
            waited_for += 1

        if waited_for >= 10:
            raise RuntimeError("Failed to return successful request")

        assert data["content"]["common_name"] == "Water"

    def test_bad_casrn(self):
        casrn = "1-1-1"
        url = reverse("assessment:casrn_detail", args=(casrn,))

        assert url == "/assessment/casrn/1-1-1/"

        # first time, acknowledge request
        client = APIClient()
        resp = client.get(url)
        data = resp.json()
        assert data == {"status": "requesting"}

        # wait until failure
        waited_for = 0
        while waited_for < 10:
            resp = client.get(url)
            data = resp.json()
            if data["status"] == "failed":
                break

            time.sleep(1)
            waited_for += 1

        if waited_for >= 10:
            raise RuntimeError("Failed to return incorrect request")

        assert data == {"status": "failed", "content": {}}


@pytest.mark.django_db
class TestDatasetViewset:
    def test_permissions(self, db_keys):
        client = APIClient()

        # team-member can view anything, including versions
        assert client.login(username="team@team.com", password="pw") is True
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 200),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 200),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

        # reviewers can only view final versions
        assert client.login(username="rev@rev.com", password="pw") is True
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 403),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

        # unauthenticated can view public final but not private or versions
        client = APIClient()
        for url, code in [
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)), 200),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_final, 1)), 403),
            (reverse("assessment:api:dataset-detail", args=(db_keys.dataset_working,)), 403),
            (reverse("assessment:api:dataset-data", args=(db_keys.dataset_working,)), 403),
            (reverse("assessment:api:dataset-version", args=(db_keys.dataset_working, 1)), 403),
        ]:
            resp = client.get(url)
            assert resp.status_code == code

    def test_response_data(self, db_keys):
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        # ensure we get expected response
        url = reverse("assessment:api:dataset-data", args=(db_keys.dataset_final,)) + "?format=json"
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()[0]["sepal_length"] == 5.1

    def test_response_version(self, db_keys):
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

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
class TestLogViewset:
    def test_permissions(self, db_keys):
        client = APIClient()

        # only admin can view list of global logs
        url = reverse("assessment:api:logs-list")

        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

    def test_list(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:logs-list")

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the list should only show global logs for admins
        assert len(resp.json()) == 1
        expected = {"message": "Global log", "assessment": None}
        assert expected.items() <= resp.json()[0].items()

    def test_assessment(self, db_keys):
        """
        Technically this endpoint is under AssessmentViewset, but
        due to its log functionality is included here
        """
        url = reverse("assessment:api:assessment-logs", args=(db_keys.assessment_working,))
        client = APIClient()
        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the response should be a list of all logs for this assessment
        assert len(resp.json()) == 1
        expected = {"message": "Assessment log", "assessment": db_keys.assessment_working}
        assert expected.items() <= resp.json()[0].items()
