
import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestOptionalTrailingSlashRouter:
    """
    Test the OptionalTrailingSlashRouter.

    We'll test the `StudyCleanupFieldsView` since it's a fully parameterized implementation of
    this base class.
    """

    def test_same_result(self, db_keys):
        # check that we get the same result with or without a trailing slash

        url1 = reverse("study:api:study-detail", args=(db_keys.study_final_bioassay,))
        url2 = url1 + "/"

        client = APIClient()

        resp1 = client.get(url1)
        resp2 = client.get(url2)

        assert url1 == '/study/api/study/7'
        assert url2 == '/study/api/study/7/'

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        assert resp1.json() == resp2.json()


@pytest.mark.django_db
class TestCleanupFieldsBaseViewSet:
    """
    Test the CleanupFieldBaseViewset.

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
        assert client.login(username="team@team.com", password="pw") is True
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
        assert client.login(username="team@team.com", password="pw") is True
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
        assert client.login(username="team@team.com", password="pw") is True
        resp = client.patch(url + f"?assessment_id={db_keys.assessment_final}")
        assert resp.status_code == 403

        # check success missing header
        resp = client.patch(url + f"?assessment_id={db_keys.assessment_working}")
        assert resp.status_code == 400
        assert "Header 'X-CUSTOM-BULK-OPERATION' should be provided" in resp.json()["detail"]

    def test_patch(self, db_keys):
        url = reverse("study:api:study-cleanup-list")
        client = APIClient()

        assert client.login(username="team@team.com", password="pw") is True

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
