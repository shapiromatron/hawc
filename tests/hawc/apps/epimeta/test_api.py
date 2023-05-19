import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestAssessmentViewSet:
    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("meta:api:assessment-export", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = Path(DATA_ROOT / "api-epimeta-assessment-export.json")
        url = (
            reverse("meta:api:assessment-export", args=(db_keys.assessment_final,)) + "?format=json"
        )

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2, sort_keys=True))

        assert data == json.loads(fn.read_text())
