import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewset:
    def _test_flat_export(self, rewrite_data_files: bool, fn: str, url: str):

        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        path = Path(DATA_ROOT / fn)
        data = resp.json()

        if rewrite_data_files:
            path.write_text(json.dumps(data, indent=2))

        assert data == json.loads(path.read_text())

    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("epi:api:assessment-export", args=(db_keys.assessment_working,)),
            reverse("epi:api:assessment-study-heatmap", args=(db_keys.assessment_working,)),
            reverse("epi:api:assessment-result-heatmap", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-epi-assessment-export.json"
        url = reverse(f"epi:api:assessment-export", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-study-heatmap-unpublished-False.json"
        url = reverse(f"epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-study-heatmap-unpublished-True.json"
        url = (
            reverse(f"epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_result_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-result-heatmap-unpublished-False.json"
        url = reverse(f"epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-result-heatmap-unpublished-True.json"
        url = (
            reverse(f"epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)
