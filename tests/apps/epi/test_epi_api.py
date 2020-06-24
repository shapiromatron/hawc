import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewset:
    def _test_epi_export(
        self,
        rewrite_data_files: bool,
        url_path: str,
        file_slug: str,
        key: int,
        query_string: str = "",
    ):
        # Add json format to query string
        if query_string:
            query_string += "&format=json"
        else:
            query_string = "?format=json"

        fn = Path(DATA_ROOT / f"api-epi-assessment-{file_slug}.json")
        url = reverse(f"epi:api:assessment-{url_path}", args=(key,)) + query_string

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
        self._test_epi_export(rewrite_data_files, "export", "export", db_keys.assessment_final)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_epi_export(
            rewrite_data_files,
            "study-heatmap",
            "study-heatmap-unpublished-True",
            db_keys.assessment_final,
            "?unpublished=True",
        )
        self._test_epi_export(
            rewrite_data_files,
            "study-heatmap",
            "study-heatmap-unpublished-False",
            db_keys.assessment_final,
            "?unpublished=False",
        )

    def test_result_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_epi_export(
            rewrite_data_files,
            "result-heatmap",
            "result-heatmap-unpublished-True",
            db_keys.assessment_final,
            "?unpublished=True",
        )
        self._test_epi_export(
            rewrite_data_files,
            "result-heatmap",
            "result-heatmap-unpublished-False",
            db_keys.assessment_final,
            "?unpublished=False",
        )
