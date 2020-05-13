import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestAssessmentViewset:
    def _test_animal_export(self, rewrite_data_files: bool, slug: str, key: int):
        fn = Path(DATA_ROOT / f"api-animal-assessment-{slug}.json")
        url = reverse(f"animal:api:assessment-{slug}", args=(key,)) + "?format=json"

        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2))

        assert data == json.loads(fn.read_text())

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        self._test_animal_export(rewrite_data_files, "full-export", db_keys.assessment_final)

    def test_endpoint_export(self, rewrite_data_files: bool, db_keys):
        self._test_animal_export(rewrite_data_files, "endpoint-export", db_keys.assessment_final)
