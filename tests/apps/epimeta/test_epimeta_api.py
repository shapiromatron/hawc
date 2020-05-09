import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parent / "data"


@pytest.mark.django_db
class TestAssessmentViewset:
    def test_full_export(self, db_keys):
        fn = Path(DATA_ROOT / f"api-assessment-epimeta-export.json")
        url = (
            reverse("meta:api:assessment-export", args=(db_keys.assessment_final,)) + "?format=json"
        )

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        # Path(fn).write_text(json.dumps(data, indent=2))
        assert data == json.loads(fn.read_text())
