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


@pytest.mark.django_db
class TestAnimalGroupCreateApi:
    def test_permissions(self, db_keys):
        url = reverse("animal:api:animal_group-list")
        data = {
            "name": "Animal group name",
            "species": 1,
            "strain": 1,
            "sex": "M",
            "experiment_id": 1,
        }

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
        url = reverse("animal:api:animal_group-list")
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        # payload needs to include name, species, strain, and sex
        data = {"experiment_id": 1}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name", "species", "strain", "sex"}.issubset((response.data.keys()))

        # payload needs experiment id
        data = {"name": "Animal group name", "species": 1, "strain": 1, "sex": "M"}
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data["non_field_errors"][0]) == "Expected 'experiment' or 'experiment_id'."
        )

    def test_valid_requests(self, db_keys):
        url = reverse("animal:api:animal_group-list")
        data = {
            "name": "Animal group name",
            "species": 1,
            "strain": 1,
            "sex": "M",
            "experiment_id": 1,
        }

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 201

        assert len(models.AnimalGroup.objects.filter(name="Animal group name")) == 1

        response = client.post(url, data)
        assert response.status_code == 201
        assert len(models.AnimalGroup.objects.filter(name="Animal group name")) == 2

    def test_create_dosing_regime(self, db_keys):
        url = reverse("animal:api:animal_group-list")
        data = {
            "name": "Animal group name",
            "species": 1,
            "strain": 1,
            "sex": "M",
            "experiment_id": 1,
            "dosing_regime": {
                "doses": [
                    {"dose_group_id": 0, "dose": 1.0, "dose_units_id": 1},
                    {"dose_group_id": 1, "dose": 2.0, "dose_units_id": 1},
                ],
                "route_of_exposure": "OR",
            },
        }

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data, format="json")

        assert response.status_code == 201

        animal_groups = models.AnimalGroup.objects.filter(name="Animal group name")
        assert len(animal_groups) == 1
        animal_group = animal_groups[0]

        assert len(animal_group.dosing_regime.doses.all()) == 2

    def test_reference_dosing_regime(self, db_keys):
        url = reverse("animal:api:animal_group-list")
        data = {
            "name": "Animal group name",
            "species": 1,
            "strain": 1,
            "sex": "M",
            "experiment_id": 1,
            "dosing_regime_id": 1,
        }

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data, format="json")

        assert response.status_code == 201


@pytest.mark.django_db
class TestEndpointCreateApi:
    def test_permissions(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        data = {"name": "Endpoint name", "animal_group_id": 1}

        # reviewers shouldn't be able to create
        client = APIClient()
        assert client.login(username="rev@rev.com", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 403

        # public shouldn't be able to create
        client = APIClient()
        response = client.post(url, data)
        assert response.status_code == 403

    def test_bad_requests(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        # payload needs to include name
        data = {"animal_group_id": 1}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name"}.issubset((response.data.keys()))

        # payload needs animal group id
        data = {"name": "Endpoint name"}
        response = client.post(url, data)
        assert response.status_code == 400
        assert (
            str(response.data["non_field_errors"][0])
            == "Expected 'animal_group' or 'animal_group_id'."
        )

    def test_valid_requests(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        data = {"name": "Endpoint name", "animal_group_id": 1}

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data)
        assert response.status_code == 201

        assert len(models.Endpoint.objects.filter(name="Endpoint name")) == 1

        response = client.post(url, data)
        assert response.status_code == 201
        assert len(models.Endpoint.objects.filter(name="Endpoint name")) == 2

    def test_endpoint_groups_create(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
            "groups": [{"dose_group_id": 0, "n": 1}, {"dose_group_id": 1, "n": 2}],
        }

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 201

        endpoints = models.Endpoint.objects.filter(name="Endpoint name")
        assert len(endpoints) == 1
        endpoint = endpoints[0]

        assert len(endpoint.groups.all()) == 2
