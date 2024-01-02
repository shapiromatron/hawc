import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from ..test_utils import check_api_json_data


@pytest.mark.django_db
class TestIVAssessmentViewSet:
    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("invitro:api:assessment-full-export", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-invitro-assessment-full-export.json"
        url = (
            reverse("invitro:api:assessment-full-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200
        check_api_json_data(resp.json(), fn, rewrite_data_files)
