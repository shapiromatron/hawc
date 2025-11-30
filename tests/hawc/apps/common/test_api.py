import json

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIClient

from hawc.apps.assessment.api import user_can_edit_object
from hawc.apps.common.diagnostics import worker_healthcheck
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study.models import Study

from ..test_utils import check_details_of_last_log_entry


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


@pytest.mark.django_db
class TestCleanupFieldsBaseViewSet:
    """
    Test the CleanupFieldBaseViewSet.

    We'll test the `StudyCleanupFieldsView` since it's a fully parameterized implementation of
    this base class.
    """

    def test_list(self, db_keys):
        url = reverse("study:api:study-cleanup-list")
        client = APIClient()

        # check `assessment_id` requirement
        resp = client.get(url)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "Please provide an `assessment_id` argument to your GET request."
        }

        # check anon user
        resp = client.get(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 403

        # check that even team-members can't edit if project is not editable
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url + f"?assessment_id={db_keys.assessment_final}")
        assert resp.status_code == 403

        # check success case
        resp = client.get(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == 1

    def test_fields(self, db_keys):
        url = reverse("study:api:study-cleanup-fields")
        client = APIClient()

        # check `assessment_id` requirement
        resp = client.get(url)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "Please provide an `assessment_id` argument to your GET request."
        }

        # check anon user
        resp = client.get(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 403

        # check that even team-members can't edit if project is not editable
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url + f"?assessment_id={db_keys.assessment_final}")
        assert resp.status_code == 403

        # check success case
        resp = client.get(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 200
        assert set(resp.json()["text_cleanup_fields"]) == set(Study.TEXT_CLEANUP_FIELDS)

    def test_patch_permissions(self, db_keys):
        url = reverse("study:api:study-cleanup-list")
        client = APIClient()

        # check `assessment_id` requirement
        resp = client.patch(url)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "Please provide an `assessment_id` argument to your GET request."
        }

        # check anon user
        resp = client.patch(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 403

        # check that even team-members can't edit if project is not editable
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.patch(url + f"?assessment_id={db_keys.assessment_final}")
        assert resp.status_code == 403

        # check success missing header
        resp = client.patch(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 400
        assert "Header 'X-CUSTOM-BULK-OPERATION' should be provided" in resp.json()["detail"]

    def test_patch(self, db_keys):
        url = reverse("study:api:study-cleanup-list")
        client = APIClient()

        assert client.login(username="team@hawcproject.org", password="pw") is True

        new_short_citation = "ABC"
        assert Study.objects.filter(short_citation=new_short_citation).count() == 0

        # check no success with no ids
        resp = client.patch(
            url + f"?assessment_id={db_keys.assessment_working}",
            json.dumps({"short_citation": new_short_citation}),
            content_type="application/json",
            **{"HTTP_X_CUSTOM_BULK_OPERATION": "true"},
        )
        assert resp.status_code == 204
        assert Study.objects.filter(short_citation=new_short_citation).count() == 0

        # check no success with id not in assessment
        study_id = db_keys.study_final_bioassay
        assert Study.objects.get(id=study_id).short_citation != new_short_citation
        resp = client.patch(
            url + f"?assessment_id={db_keys.assessment_working}&ids={study_id}",
            json.dumps({"short_citation": new_short_citation}),
            content_type="application/json",
            **{"HTTP_X_CUSTOM_BULK_OPERATION": "true"},
        )
        assert resp.status_code == 403
        assert Study.objects.get(id=study_id).short_citation != new_short_citation

        # check too long
        study_id = db_keys.study_working
        resp = client.patch(
            url + f"?assessment_id={db_keys.assessment_working}&ids={study_id}",
            json.dumps({"short_citation": "a" * 500}),
            content_type="application/json",
            **{"HTTP_X_CUSTOM_BULK_OPERATION": "true"},
        )
        assert resp.status_code == 400
        assert "value too long" in resp.json()["detail"]

        # finally, check success
        study_id = db_keys.study_working
        assert Study.objects.get(id=study_id).short_citation != new_short_citation
        resp = client.patch(
            url + f"?assessment_id={db_keys.assessment_working}&ids={study_id}",
            json.dumps({"short_citation": new_short_citation}),
            content_type="application/json",
            **{"HTTP_X_CUSTOM_BULK_OPERATION": "true"},
        )
        assert resp.status_code == 204
        assert Study.objects.get(id=study_id).short_citation == new_short_citation
        check_details_of_last_log_entry(study_id, "Updated study.study")


@pytest.mark.django_db
def test_user_can_edit_object(db_keys):
    user = HAWCUser.objects.get(email="team@hawcproject.org")

    working = Study.objects.get(id=db_keys.study_working)
    assert user_can_edit_object(working, user) is True

    final = Study.objects.get(id=db_keys.study_final_bioassay)
    assert user_can_edit_object(final, user) is False
    with pytest.raises(PermissionDenied):
        user_can_edit_object(final, user, raise_exception=True)


@pytest.mark.django_db
class TestHealthcheckViewSet:
    def test_web(self):
        client = APIClient()
        url = reverse("common:api:healthcheck-web")
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json() == {"healthy": True}

    @pytest.mark.skipif(not has_redis(), reason="skip; redis cache required")
    def test_worker(self):
        client = APIClient()
        url = reverse("common:api:healthcheck-worker")

        # no data; should be an error
        resp = client.get(url)
        assert resp.status_code == 400
        assert resp.json()["healthy"] is False

        # has recent data; should be healthy
        worker_healthcheck.push()
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["healthy"] is True
