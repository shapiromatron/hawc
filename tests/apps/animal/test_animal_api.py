import json
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.animal import models

DATA_ROOT = Path(__file__).parents[2] / "data/api"


@pytest.mark.django_db
class TestAssessmentViewset:
    def _test_flat_export(self, rewrite_data_files: bool, fn: str, url: str):

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
            reverse(
                "animal:api:assessment-endpoint-doses-heatmap", args=(db_keys.assessment_working,)
            ),
            reverse("animal:api:assessment-endpoints", args=(db_keys.assessment_working,)),
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
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_endpoint_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoint-export.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_endpoints(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoints.json"
        url = (
            reverse(f"animal:api:assessment-endpoints", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):

        # published
        fn = "api-animal-assessment-study-heatmap-unpublished-False.json"
        url = (
            reverse(f"animal:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-animal-assessment-study-heatmap-unpublished-True.json"
        url = (
            reverse(f"animal:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_endpoint_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-animal-assessment-endpoint-heatmap-unpublished-False.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-heatmap", args=(db_keys.assessment_final,))
            + "?format=json"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-animal-assessment-endpoint-heatmap-unpublished-True.json"
        url = (
            reverse(f"animal:api:assessment-endpoint-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_endpoint_doses_heatmap(self, rewrite_data_files: bool, db_keys):
        fn = "api-animal-assessment-endpoint-doses-heatmap.json"
        url = (
            reverse(
                f"animal:api:assessment-endpoint-doses-heatmap", args=(db_keys.assessment_final,)
            )
            + "?format=json"
        )
        self._test_flat_export(rewrite_data_files, fn, url)


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

        first_animal_group = models.AnimalGroup.objects.filter(name="Animal group name")[0]
        data["sibling_id"] = first_animal_group.id

        response = client.post(url, data, format="json")
        assert response.status_code == 201
        assert len(models.AnimalGroup.objects.filter(name="Animal group name")) == 2

        assert models.AnimalGroup.objects.filter(
            name="Animal group name", siblings_id=first_animal_group.id
        ).exists()

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
        expected_data = {
            "name": "Animal group name",
            "species_id": 1,
            "strain_id": 1,
            "sex": "M",
            "experiment_id": 1,
        }
        assert set(expected_data.items()).issubset(set(animal_group.__dict__.items()))

        dosing_regime = animal_group.dosing_regime
        expected_data = {"route_of_exposure": "OR"}
        assert set(expected_data.items()).issubset(set(dosing_regime.__dict__.items()))

        doses = dosing_regime.doses.all()
        assert len(doses) == 2

        dose_1 = doses[0]
        expected_data = {
            "dose_regime_id": dosing_regime.id,
            "dose_units_id": 1,
            "dose_group_id": 0,
            "dose": 1.0,
        }
        assert set(expected_data.items()).issubset(set(dose_1.__dict__.items()))

        dose_2 = doses[1]
        expected_data = {
            "dose_regime_id": dosing_regime.id,
            "dose_units_id": 1,
            "dose_group_id": 1,
            "dose": 2.0,
        }
        assert set(expected_data.items()).issubset(set(dose_2.__dict__.items()))

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
        expected_data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
        }
        assert set(expected_data.items()).issubset(set(endpoint.__dict__.items()))

        groups = endpoint.groups.all()
        assert len(groups) == 2

        group_1 = groups[0]
        expected_data = {"endpoint_id": endpoint.id, "dose_group_id": 0, "n": 1}
        assert set(expected_data.items()).issubset(set(group_1.__dict__.items()))

        group_2 = groups[1]
        expected_data = {"endpoint_id": endpoint.id, "dose_group_id": 1, "n": 2}
        assert set(expected_data.items()).issubset(set(group_2.__dict__.items()))
