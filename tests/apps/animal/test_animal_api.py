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

    def _test_heatmap(self, rewrite_data_files: bool, slug: str, key: int, published: bool):
        fn = Path(DATA_ROOT / f"api-animal-assessment-{slug}-published-{published}.json")
        url = reverse(f"animal:api:assessment-{slug}", args=(key,)) + f"?format=json&published={published}"
        import pdb

        pdb.set_trace()

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
            reverse("animal:api:assessment-full-export", args=(db_keys.assessment_working,)),
            reverse("animal:api:assessment-endpoint-export", args=(db_keys.assessment_working,)),
            reverse("animal:api:assessment-endpoint-heatmap", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        self._test_animal_export(rewrite_data_files, "full-export", db_keys.assessment_final)

    def test_endpoint_export(self, rewrite_data_files: bool, db_keys):
        self._test_animal_export(rewrite_data_files, "endpoint-export", db_keys.assessment_final)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_heatmap(rewrite_data_files, "study-heatmap", db_keys.assessment_working, True)
        self._test_heatmap(rewrite_data_files, "study-heatmap", db_keys.assessment_working, False)

    def test_endpoint_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_heatmap(rewrite_data_files, "endpoint-heatmap", db_keys.assessment_working, True)
        self._test_heatmap(rewrite_data_files, "endpoint-heatmap", db_keys.assessment_working, False)
