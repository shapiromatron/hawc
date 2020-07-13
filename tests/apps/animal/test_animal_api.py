import json
from copy import deepcopy
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.animal import forms, models

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

        # empty payload doesn't crash
        data = {}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name", "type"}.issubset((response.data.keys()))

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
        assert response.json() == {"study_id": ["study_id is required."]}

        # purity check
        data = {
            "name": "Experiment name",
            "type": "NR",
            "study_id": db_keys.study_working,
            "purity_available": True,
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {
            "purity_qualifier": ["Qualifier must be specified"],
            "purity": ["A purity value must be specified"],
        }

        data = {
            "name": "Experiment name",
            "type": "NR",
            "study_id": db_keys.study_working,
            "purity_available": True,
            "purity_qualifier": ">",
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"purity": ["A purity value must be specified"]}

        data = {
            "name": "Experiment name",
            "type": "NR",
            "study_id": db_keys.study_working,
            "purity_available": False,
            "purity_qualifier": ">",
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {
            "purity_qualifier": ["Qualifier must be blank if purity is not available"]
        }

        data = {
            "name": "Experiment name",
            "type": "NR",
            "study_id": db_keys.study_working,
            "purity_available": False,
            "purity": 0.84,
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"purity": ["Purity must be blank if purity is not available"]}

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
            "dosing_regime_id": 1,
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

        # empty payload doesn't crash
        data = {}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name", "species", "strain", "sex"}.issubset((response.data.keys()))

        # payload needs to include name, species, strain, and sex
        data = {"experiment_id": 1}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name", "species", "strain", "sex"}.issubset((response.data.keys()))

        # payload needs experiment id
        data = {"name": "Animal group name", "species": 1, "strain": 1, "sex": "M"}
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"experiment_id": ["experiment_id is required."]}

        # payload needs dosing_regime_id
        data = {
            "experiment_id": 1,
            "name": "Animal group name",
            "species": 1,
            "strain": 1,
            "sex": "M",
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"dosing_regime_id": ["dosing_regime_id is required."]}

        # strain not from species
        data = {
            "experiment_id": 1,
            "dosing_regime_id": 1,
            "name": "Animal group name",
            "species": 2,
            "strain": 1,
            "sex": "M",
        }
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"strain": ["Selected strain is not of the selected species."]}

    def test_valid_requests(self, db_keys):
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
        response = client.post(url, data)
        assert response.status_code == 201
        animal_group = models.AnimalGroup.objects.get(id=response.json()["id"])

        # test relations
        data.update(dict(siblings_id=animal_group.id, parent_ids=[animal_group.id],))
        response = client.post(url, data, format="json")
        assert response.status_code == 201
        assert models.AnimalGroup.objects.filter(name=data["name"]).count() == 2

        animal_group_2 = models.AnimalGroup.objects.get(id=response.json()["id"])
        assert animal_group_2.siblings == animal_group
        parents = animal_group_2.parents.all()
        assert parents.count() == 1
        assert parents[0] == animal_group

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

        # empty payload doesn't crash
        data = {}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name"}.issubset((response.data.keys()))

        # payload needs to include name
        data = {"animal_group_id": 1}
        response = client.post(url, data)
        assert response.status_code == 400
        assert {"name"}.issubset((response.data.keys()))

        # payload needs animal group id
        data = {"name": "Endpoint name"}
        response = client.post(url, data)
        assert response.status_code == 400
        assert response.json() == {"animal_group_id": ["animal_group_id is required."]}

    def test_form_clean_endpoint_called(self, db_keys):
        # ensure forms.EndpointForm.clean_endpoint is called (tested elsewhere)
        url = reverse("animal:api:endpoint-list")
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
            "data_type": "C",
            "variance_type": 1,
            "response_units": "μg/dL",
            "observation_time": 1,
            "observation_time_units": 0,
        }
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {
            "observation_time_units": [forms.EndpointForm.OBS_TIME_UNITS_REQ]
        }

    def test_valid_requests(self, db_keys):
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        url = reverse("animal:api:endpoint-list")
        data = {"name": "Endpoint name", "animal_group_id": 1, "data_type": "C", "variance_type": 1}

        assert models.Endpoint.objects.filter(name=data["name"]).count() == 0
        response = client.post(url, data)
        assert response.status_code == 201
        assert models.Endpoint.objects.filter(name=data["name"]).count() == 1

    def test_endpoint_groups_create(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
            "data_type": "C",
            "variance_type": 1,
            "response_units": "μg/dL",
            "groups": [
                {"dose_group_id": 0, "n": 1},
                {"dose_group_id": 1, "n": 2},
                {"dose_group_id": 2, "n": 2},
            ],
        }

        # valid request
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 201

        endpoints = models.Endpoint.objects.filter(name=data["name"])
        assert endpoints.count() == 1

        endpoint = endpoints[0]
        assert endpoint.animal_group_id == data["animal_group_id"]

        groups = endpoint.groups.all()
        assert groups.count() == 3

        group_1 = groups[0]
        expected_data = {"endpoint_id": endpoint.id, "dose_group_id": 0, "n": 1}
        assert set(expected_data.items()).issubset(set(group_1.__dict__.items()))

        group_2 = groups[1]
        expected_data = {"endpoint_id": endpoint.id, "dose_group_id": 1, "n": 2}
        assert set(expected_data.items()).issubset(set(group_2.__dict__.items()))

    def test_endpoint_groups_check(self, db_keys):
        url = reverse("animal:api:endpoint-list")
        client = APIClient()
        valid_data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
            "data_type": "C",
            "variance_type": 1,
            "response_units": "μg/dL",
            "LOEL": -999,
            "groups": [
                {"dose_group_id": 0, "n": 1},
                {"dose_group_id": 1, "n": 2},
                {"dose_group_id": 2, "n": 2},
            ],
        }
        assert client.login(username="team@team.com", password="pw") is True

        # valid request
        response = client.post(url, valid_data, format="json")
        assert response.status_code == 201

        # 3 groups required
        data = deepcopy(valid_data)
        data["groups"] = [{"dose_group_id": 0, "n": 1}]
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["If entering groups, all 3 must be entered"]
        }

        # wrong dose_group_ids
        data = deepcopy(valid_data)
        data["groups"] = [
            {"dose_group_id": 1, "n": 1},
            {"dose_group_id": 2, "n": 2},
            {"dose_group_id": 3, "n": 2},
        ]
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["For groups, `dose_group_id` must include all values in [0, 1, 2]"]
        }

        # wrong value for LOEL
        data = deepcopy(valid_data)
        data["LOEL"] = 3
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["LOEL must be -999 or in [0, 1, 2]"]}

    def test_form_clean_endpoint_endpoint_called(self, db_keys):
        # ensure forms.EndpointGroupForm.clean_endpoint is called (tested elsewhere)
        url = reverse("animal:api:endpoint-list")
        client = APIClient()
        assert client.login(username="team@team.com", password="pw") is True

        data = {
            "name": "Endpoint name",
            "animal_group_id": 1,
            "data_type": "D",
            "variance_type": 0,
            "response_units": "incidence",
            "groups": [
                {"dose_group_id": 0, "n": 1, "incidence": 1},
                {"dose_group_id": 1, "n": 1, "incidence": 1},
                {"dose_group_id": 2, "n": 1, "incidence": 2},
            ],
        }
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {
            "groups": [{}, {}, {"incidence": ["Incidence must be less-than or equal-to N"]}]
        }
