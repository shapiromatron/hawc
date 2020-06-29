import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestAssessmentViewset:
    def _test_animal_export(self, rewrite_data_files: bool, fn: str, url: str):

        client = APIClient()
        assert client.login(username="rev@rev.com", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        path = Path(DATA_ROOT / fn)
        data = resp.json()

        if rewrite_data_files:
            path.write_text(json.dumps(data, indent=2))

        assert data == json.loads(path.read_text())

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
        fn = "api-animal-assessment-full-export.json"
        url = (
            reverse(f"animal:api:assessment-full-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

    def test_endpoint_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoint-export.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

    def test_endpoints(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoints.json"
        url = (
            reverse(f"animal:api:assessment-endpoints", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):

        # published
        fn = "api-animal-assessment-study-heatmap-unpublished-False.json"
        url = (
            reverse(f"animal:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-animal-assessment-study-heatmap-unpublished-True.json"
        url = (
            reverse(f"animal:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

    def test_endpoint_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-animal-assessment-endpoint-heatmap-unpublished-False.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-heatmap", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-animal-assessment-endpoint-heatmap-unpublished-True.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_animal_export(rewrite_data_files, fn, url)

    def test_endpoint_doses_heatmap(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoint-doses-heatmap.json"
        url = (
            reverse(
                f"animal:api:assessment-endpoint-doses-heatmap", args=(db_keys.assessment_final,)
            )
            + "?format=json"
        )
        self._test_animal_export(rewrite_data_files, fn, url)
