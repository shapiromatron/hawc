import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animalv2 import models
from hawc.apps.assessment import models as assessment_models


@pytest.mark.django_db
class TestExperimentChildren:
    def _test_helper(self, client, experiment, clazz, input_payload, short_name):
        initial_count = clazz.objects.count()
        name_val = input_payload["name"]
        expected_template = f"animalv2/fragments/_{short_name}_row.html"

        # create
        url = reverse(f"animalv2:{short_name}-create", args=[experiment.id])
        resp = client.post(url, data=input_payload)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val}</td>" in str(resp.content)
        created_obj = resp.context["object"]
        assert f"{short_name}-{created_obj.id}" in str(resp.content)
        assert clazz.objects.count() == initial_count + 1

        # clone
        url = reverse(f"animalv2:{short_name}-clone", args=[created_obj.id])
        resp = client.post(url)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val} (2)</td>" in str(resp.content)
        assert clazz.objects.count() == initial_count + 2

        # read
        url = reverse(f"animalv2:{short_name}-detail", args=[created_obj.id])
        resp = client.get(url)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val}</td>" in str(resp.content)
        assert clazz.objects.count() == initial_count + 2

        # update
        url = reverse(f"animalv2:{short_name}-update", args=[created_obj.id])
        input_payload["name"] = f"{name_val} update"
        resp = client.post(url, data=input_payload)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val} update</td>" in str(resp.content)
        assert f"{short_name}-{created_obj.id}" in str(resp.content)
        assert clazz.objects.count() == initial_count + 2

    def test_children(self, db_keys):
        experiment_id = db_keys.epiv2_design
        experiment = models.Experiment.objects.get(id=experiment_id)
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        # Chemical
        dsstox_id = assessment_models.DSSTox.objects.first().dtxsid
        inputs = {
            "name": "ex chemical",
            "dtxsid": dsstox_id,
        }
        self._test_helper(client, experiment, models.Chemical, inputs, "chemical")

        # Animal Group
        strain = assessment_models.Strain.objects.first()
        species = assessment_models.Species.objects.get(pk=strain.species.id)
        inputs = {
            "name": "ex animalgroup",
            "species": species.id,
            "strain": strain.id,
            "sex": "M",
        }
        self._test_helper(client, experiment, models.AnimalGroup, inputs, "animalgroup")

        # TODO -- add sample payloads for all the other htmx forms...
