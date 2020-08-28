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
class TestJobViewset:
    def test_permissions(self, db_keys):
        client = APIClient()

        # only admin can view list of global jobs
        url = reverse("assessment:api:jobs-list")

        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # assessment level permissions apply to job retrieve with associated assessment
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_assessment,))

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="team@team.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # assessment level permissions apply to job create with associated assessment
        url = reverse("assessment:api:jobs-list")
        data = {"assessment": db_keys.assessment_working}

        client = APIClient()
        resp = client.post(url, data)
        assert resp.status_code == 403

        assert client.login(username="team@team.com", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 201

        # only admin can retrieve a global job
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_global,))

        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # only admin can create a global job
        url = reverse("assessment:api:jobs-list")
        data = {"assessment": ""}

        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 403

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 201

    def test_list(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-list")

        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the list should only show global jobs for admins
        assert len(resp.json()) == 1
        expected = {"task_id": db_keys.job_global, "assessment": None}
        assert expected.items() <= resp.json()[0].items()

    def test_detail(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_assessment,))

        assert client.login(username="team@team.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the response should be details of the job
        expected = {"task_id": db_keys.job_assessment, "assessment": db_keys.assessment_working}
        assert expected.items() <= resp.json().items()

    def test_create(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-list")

        # on create, details of the created job is returned
        assert client.login(username="sudo@sudo.com", password="pw") is True
        resp = client.post(url)
        assert resp.status_code == 201

        expected = {
            "assessment": None,
            "status": "PENDING",
            "job": "TEST",
            "kwargs": {},
            "result": {},
        }
        assert expected.items() <= resp.json().items()

        # detail_url can be used to check on status of created job
        url = resp.json()["detail_url"]
        resp = client.get(url)
        expected = {"status": "SUCCESS", "result": {"data": "SUCCESS"}}
        assert expected.items() <= resp.json().items()

    def test_assessment(self, db_keys):
        """
        Technically this endpoint is under AssessmentViewset, but
        due to its job functionality is included here
        """
        url = reverse("assessment:api:assessment-jobs", args=(db_keys.assessment_working,))
        client = APIClient()
        assert client.login(username="pm@pm.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the response should be a list of all jobs for this assessment
        assert len(resp.json()) == 1
        expected = {"task_id": db_keys.job_assessment, "assessment": db_keys.assessment_working}
        assert expected.items() <= resp.json()[0].items()

        # jobs can also be created at this endpoint
        post_resp = client.post(url)
        assert post_resp.status_code == 201
        get_resp = client.get(url)
        assert len(get_resp.json()) == 2
        expected = {
            "task_id": post_resp.json()["task_id"],
            "assessment": db_keys.assessment_working,
        }
        assert expected.items() <= get_resp.json()[0].items()

