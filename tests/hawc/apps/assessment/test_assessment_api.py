from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture(scope="module")
def media_file():
    fn = Path(settings.MEDIA_ROOT) / "test.txt"
    if not fn.exists():
        fn.write_text("hello\n")


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
class TestJobViewset:
    def test_permissions(self, db_keys):
        client = APIClient()

        # only admin can view list of global jobs
        url = reverse("assessment:api:jobs-list")

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # assessment level permissions apply to job retrieve with associated assessment
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_assessment,))

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # assessment level permissions apply to job create with associated assessment
        url = reverse("assessment:api:jobs-list")
        data = {"assessment": db_keys.assessment_working}

        client = APIClient()
        resp = client.post(url, data)
        assert resp.status_code == 403

        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 201

        # only admin can retrieve a global job
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_global,))

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # only admin can create a global job
        url = reverse("assessment:api:jobs-list")
        data = {"assessment": ""}

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 403

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.post(url, data)
        assert resp.status_code == 201

    def test_list(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-list")

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the list should only show global jobs for admins
        assert len(resp.json()) == 1
        expected = {"task_id": db_keys.job_global, "assessment": None}
        assert expected.items() <= resp.json()[0].items()

    def test_detail(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-detail", args=(db_keys.job_assessment,))

        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the response should be details of the job
        expected = {"task_id": db_keys.job_assessment, "assessment": db_keys.assessment_working}
        assert expected.items() <= resp.json().items()

    def test_create(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:jobs-list")

        # on create, details of the created job is returned
        assert client.login(username="admin@hawcproject.org", password="pw") is True
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
        assert client.login(username="pm@hawcproject.org", password="pw") is True
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


@pytest.mark.django_db
class TestLogViewset:
    def test_permissions(self, db_keys):
        client = APIClient()

        # only admin can view list of global logs
        url = reverse("assessment:api:logs-list")

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

    def test_list(self, db_keys):
        client = APIClient()
        url = reverse("assessment:api:logs-list")

        assert client.login(username="admin@hawcproject.org", password="pw") is True
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
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # the response should be a list of all logs for this assessment
        assert len(resp.json()) == 1
        expected = {"message": "Assessment log", "assessment": db_keys.assessment_working}
        assert expected.items() <= resp.json()[0].items()


@pytest.mark.django_db
class TestDssToxViewset:
    def test_expected_response(self):
        dtxsid = "DTXSID6026296"
        client = APIClient()
        url = reverse("assessment:api:dsstox-detail", args=(dtxsid,))
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["dtxsid"] == dtxsid


@pytest.mark.django_db
class TestHealthcheckViewset:
    def test_healthcheck(self):
        client = APIClient()
        url = reverse("assessment:api:healthcheck-list")
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
class TestAdminDashboardViewset:
    def test_permissions(self):
        client = APIClient()

        # failure - not admin
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-assessment-size")
        resp = client.get(url)
        assert resp.status_code == 403

        # success - admin
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-assessment-size")
        resp = client.get(url)
        assert resp.status_code == 200

    def test_media_report(self, media_file):
        client = APIClient()
        # check that media report successfully returns a csv header
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-media") + "?format=csv"
        resp = client.get(url)
        assert resp.status_code == 200
        header = resp.content.decode().split("\n")[0]
        assert header == "name,extension,full_path,hash,uri,media_preview,size_mb,created,modified"
