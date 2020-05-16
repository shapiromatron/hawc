import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewset:
    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = Path(DATA_ROOT / f"api-epi-assessment-export.json")
        url = (
            reverse("epi:api:assessment-export", args=(db_keys.assessment_final,)) + "?format=json"
        )

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2))

        assert data == json.loads(fn.read_text())
