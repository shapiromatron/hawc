import json

import pytest
from django.forms.models import model_to_dict
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animal import constants, models

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    urls = [
        reverse("animal:experiment_new", args=(1,)),
        reverse("animal:experiment_copy", args=(1,)),
        reverse("animal:experiment_detail", args=(1,)),
        reverse("animal:experiment_update", args=(1,)),
        reverse("animal:experiment_delete", args=(1,)),
        reverse("animal:animal_group_new", args=(1,)),
        reverse("animal:animal_group_copy", args=(1,)),
        reverse("animal:animal_group_detail", args=(1,)),
        reverse("animal:animal_group_update", args=(1,)),
        reverse("animal:animal_group_delete", args=(1,)),
        reverse("animal:endpoint_copy", args=(1,)),
        reverse("animal:dosing_regime_update", args=(1,)),
        reverse("animal:endpoint_list", args=(1,)),
        reverse("animal:endpoint_new", args=(1,)),
        reverse("animal:endpoint_detail", args=(1,)),
        reverse("animal:endpoint_update", args=(1,)),
        reverse("animal:endpoint_delete", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)

    client = get_client("admin")
    urls = [
        reverse("animal:endpoint_list_v2", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestAnimalGroupCreate:
    def valid_payload(self):
        return {
            "name": "test",
            "species": "1",
            "strain": "1",
            "sex": "M",
            "route_of_exposure": "OR",
            "num_dose_groups": "3",
            "positive_control": "False",
            "negative_control": "NR",
            "dose_groups_json": json.dumps(
                [
                    {"dose_units": 1, "dose_group_id": 0, "dose": 1},
                    {"dose_units": 2, "dose_group_id": 0, "dose": 4},
                    {"dose_units": 1, "dose_group_id": 1, "dose": 2},
                    {"dose_units": 2, "dose_group_id": 1, "dose": 5},
                    {"dose_units": 1, "dose_group_id": 2, "dose": 3},
                    {"dose_units": 2, "dose_group_id": 2, "dose": 6},
                ]
            ),
        }

    def test_success(self, db_keys):
        exp = models.Experiment.objects.filter(study__assessment=db_keys.assessment_working).first()
        url = reverse("animal:animal_group_new", args=(exp.id,))

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        resp = c.get(url)
        assertTemplateUsed(resp, "animal/animalgroup_form.html")

        resp = c.post(url, self.valid_payload(), follow=True)
        assertTemplateUsed(resp, "animal/animalgroup_detail.html")
        obj = resp.context["object"]
        assert obj.name == "test"
        assert obj.dosing_regime.num_dose_groups == 3
        assert obj.dosing_regime.doses.count() == 6

    def test_bad_dose_group(self, db_keys):
        exp = models.Experiment.objects.filter(study__assessment=db_keys.assessment_working).first()
        url = reverse("animal:animal_group_new", args=(exp.id,))

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        payload = self.valid_payload()
        payload["dose_groups_json"] = '[{"dose_units": 1, "dose_group_id": 0, "dose": 0}]'
        resp = c.post(url, payload, follow=True)
        assertTemplateUsed(resp, "animal/animalgroup_form.html")
        assert "Each dose-type must have 3 dose groups" in resp.context["dose_groups_errors"]


@pytest.mark.django_db
class TestAnimalGroupUpdate:
    @pytest.mark.parametrize(
        "filter",
        [
            constants.Generation.NA,  # non generational
            constants.Generation.P0,  # generational
        ],
    )
    def test_success(self, filter):
        instance = models.AnimalGroup.objects.filter(generation=filter)[0]
        url = reverse("animal:animal_group_update", args=(instance.id,))

        c = Client()
        assert c.login(username="admin@hawcproject.org", password="pw") is True

        resp = c.get(url)
        assertTemplateUsed(resp, "animal/animalgroup_form.html")

        payload = model_to_dict(instance)
        payload.pop("siblings")
        resp = c.post(url, payload, follow=True)
        assertTemplateUsed(resp, "animal/animalgroup_detail.html")


@pytest.mark.django_db
class TestDosingRegimeUpdate:
    def valid_payload(self):
        return {
            "route_of_exposure": "OD",
            "num_dose_groups": "3",
            "positive_control": True,
            "negative_control": "VT",
            "description": "",
            "dose_groups_json": json.dumps(
                [
                    {"dose_units": 1, "dose_group_id": 0, "dose": 0},
                    {"dose_units": 2, "dose_group_id": 0, "dose": 1},
                    {"dose_units": 1, "dose_group_id": 1, "dose": 10},
                    {"dose_units": 2, "dose_group_id": 1, "dose": 2},
                    {"dose_units": 1, "dose_group_id": 2, "dose": 100},
                    {"dose_units": 2, "dose_group_id": 2, "dose": 3},
                ]
            ),
        }

    def test_success(self, db_keys):
        dr = models.DosingRegime.objects.filter(
            dosed_animals__experiment__study__assessment=db_keys.assessment_working
        ).first()
        url = reverse("animal:dosing_regime_update", args=(dr.id,))

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        assert dr.doses.count() == 3

        resp = c.get(url)
        assertTemplateUsed(resp, "animal/dosingregime_form.html")

        resp = c.post(url, self.valid_payload(), follow=True)
        assertTemplateUsed(resp, "animal/animalgroup_detail.html")
        obj = resp.context["object"]
        assert obj.dosing_regime.num_dose_groups == 3
        assert obj.dosing_regime.doses.count() == 6

    def test_bad_dose_group(self, db_keys):
        dr = models.DosingRegime.objects.filter(
            dosed_animals__experiment__study__assessment=db_keys.assessment_working
        ).first()

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        url = reverse("animal:dosing_regime_update", args=(dr.id,))
        payload = self.valid_payload()
        payload["dose_groups_json"] = '[{"dose_units": 1, "dose_group_id": 0, "dose": 0}]'
        resp = c.post(url, payload, follow=True)
        assertTemplateUsed(resp, "animal/dosingregime_form.html")
        assert "Each dose-type must have 3 dose groups" in resp.context["dose_groups_errors"]

    def test_no_dosed_animals(self):
        # with no dosed animal on a dosing regime, assert permission denied to edit
        dr = models.DosingRegime.objects.create()
        client = get_client("pm")

        url = reverse("animal:dosing_regime_update", args=(dr.id,))
        resp = client.get(url, follow=True)
        assert resp.status_code == 403

        dr.delete()


@pytest.mark.django_db
class TestEndpointCreate:
    @classmethod
    def valid_payload(cls):
        return {
            "name_term": "5",
            "name": "Fatty Acid Balance",
            "system_term": "1",
            "system": "Cardiovascular",
            "organ_term": "2",
            "organ": "Serum",
            "effect_term": "3",
            "effect": "Fatty Acids",
            "effect_subtype_term": "4",
            "effect_subtype": "Clinical Chemistry",
            "diagnostic": "",
            "observation_time": "",
            "observation_time_units": "0",
            "observation_time_text": "",
            "data_reported": "on",
            "data_extracted": "on",
            "data_type": "C",
            "variance_type": "1",
            "confidence_interval": "",
            "response_units": "units",
            "data_location": "",
            "expected_adversity_direction": "4",
            "NOEL": "0",
            "LOEL": "1",
            "FEL": "2",
            "monotonicity": "3",
            "trend_result": "3",
            "trend_value": "",
            "power_notes": "",
            "results_notes": "",
            "endpoint_notes": "",
            "litter_effects": "NA",
            "litter_effect_notes": "",
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "",
            "form-0-n": "2",
            "form-0-incidence": "",
            "form-0-response": "5",
            "form-0-variance": "2",
            "form-0-lower_ci": "",
            "form-0-upper_ci": "",
            "form-0-significance_level": "",
            "form-0-treatment_effect": "",
            "form-1-id": "",
            "form-1-n": "3",
            "form-1-incidence": "",
            "form-1-response": "6",
            "form-1-variance": "3",
            "form-1-lower_ci": "",
            "form-1-upper_ci": "",
            "form-1-significance_level": "0.05",
            "form-1-treatment_effect": "",
            "form-2-id": "",
            "form-2-n": "4",
            "form-2-incidence": "",
            "form-2-response": "7",
            "form-2-variance": "4",
            "form-2-lower_ci": "",
            "form-2-upper_ci": "",
            "form-2-significance_level": "",
            "form-2-treatment_effect": "",
        }

    def test_success(self, db_keys):
        ag = models.AnimalGroup.objects.filter(
            experiment__study__assessment=db_keys.assessment_working
        ).first()
        url = reverse("animal:endpoint_new", args=(ag.id,))

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        resp = c.get(url)
        assertTemplateUsed(resp, "animal/endpoint_form.html")

        resp = c.post(url, self.valid_payload(), follow=True)
        assertTemplateUsed(resp, "animal/endpoint_detail.html")
        obj = resp.context["object"]
        assert obj.name == "Fatty Acid Balance"
        assert obj.groups.count() == 3


@pytest.mark.django_db
class TestEndpointUpdate:
    def test_success(self, db_keys):
        endpoint = models.Endpoint.objects.filter(assessment=db_keys.assessment_working).first()
        url = reverse("animal:endpoint_update", args=(endpoint.id,))

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        assert endpoint.name == "my outcome"

        resp = c.get(url)
        assertTemplateUsed(resp, "animal/endpoint_form.html")

        payload = TestEndpointCreate.valid_payload()
        payload["form-INITIAL_FORMS"] = 3
        for i, group in enumerate(endpoint.groups.all()):
            payload[f"form-{i}-id"] = group.id

        resp = c.post(url, payload, follow=True)
        assertTemplateUsed(resp, "animal/endpoint_detail.html")
        obj = resp.context["object"]
        assert obj.name == "Fatty Acid Balance"
        assert obj.groups.count() == 3
