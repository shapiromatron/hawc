import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewset:
    def _test_heatmap(self, rewrite_data_files: bool, slug: str, key: int, unpublished: bool):
        fn = Path(DATA_ROOT / f"api-epi-assessment-{slug}-unpublished-{unpublished}.json")
        url = (
            reverse(f"epi:api:assessment-{slug}", args=(key,))
            + f"?format=json&unpublished={unpublished}"
        )

        client = APIClient()
        assert client.login(username="rev@rev.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()

        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2))

        assert data == json.loads(fn.read_text())

    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="rev@rev.com", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("epi:api:assessment-export", args=(db_keys.assessment_working,)),
            reverse("epi:api:assessment-result-heatmap", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

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

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_heatmap(rewrite_data_files, "study-heatmap", db_keys.assessment_final, True)
        self._test_heatmap(rewrite_data_files, "study-heatmap", db_keys.assessment_final, False)

    def test_result_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_heatmap(rewrite_data_files, "result-heatmap", db_keys.assessment_final, True)
        self._test_heatmap(rewrite_data_files, "result-heatmap", db_keys.assessment_final, False)
