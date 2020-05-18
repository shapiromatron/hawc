import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.animal import models

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


@pytest.mark.django_db
class TestExperimentCreateApi:
    def test_permissions(self, db_keys):
        url = reverse("animal:api:experiment-list")
        data = {"name": "Experiment name", "type": "NR", "study_id": db_keys.study_working}

        # reviewers shouldn't be able to create
        client = APIClient()
        assert client.login(username="rev@rev.com", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 403

        # public shouldn't be able to create
        client = APIClient()
        response = client.post(url, data)
        assert response.status_code == 403

    def test_bad_requests(self, db_keys):
        url = reverse("animal:api:experiment-list")
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        # payload needs to include name and type
        data = {"study_id": db_keys.study_working}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name", "type"}.issubset((response.data.keys()))

        # payload needs study id
        data = {
            "name": "Experiment name",
            "type": "NR",
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert str(response.data["non_field_errors"][0]) == "Expected 'study' or 'study_id'."

    def test_valid_requests(self, db_keys):
        url = reverse("animal:api:experiment-list")
        data = {"name": "Experiment name", "type": "NR", "study_id": db_keys.study_working}

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 201

        assert len(models.Experiment.objects.filter(name="Experiment name")) == 1

        response = client.post(url, data)
        assert response.status_code == 201
        assert len(models.Experiment.objects.filter(name="Experiment name")) == 2
