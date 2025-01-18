import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animalv2 import models
from hawc.apps.assessment import models as assessment_models


@pytest.mark.django_db
class TestStudyLevelValues:
    def test_studylevelvalues(self, db_keys):
        study_id = db_keys.study_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_studylevelvalue_count = models.StudyLevelValue.objects.count()

        # studylevelvalues create
        url = reverse("animalv2:studylevelvalues-htmx", args=[study_id, "create"])
        inputs = {
            "studylevelvalue-new-system": "System name",
            "studylevelvalue-new-value_type": 1,
            "studylevelvalue-new-value": 10,
            "studylevelvalue-new-units": 1,
            "studylevelvalue-new-comments": "a comment",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "animalv2/fragments/studylevelvalue_row.html")
        assert resp.status_code == 200
        assert "System name" in str(resp.content)
        studylevelvalue = resp.context["object"]
        assert models.StudyLevelValue.objects.count() == initial_studylevelvalue_count + 1

        # studylevelvalues read
        url = studylevelvalue.get_absolute_url()
        resp = client.get(url)
        assertTemplateUsed(resp, "animalv2/fragments/studylevelvalue_row.html")
        assert resp.status_code == 200
        assert "System name" in str(resp.content)

        # studylevelvalues update
        url = studylevelvalue.get_edit_url()
        inputs["studylevelvalue-new-system"] = "System update"
        inputs = {k.replace("new", str(studylevelvalue.id)): v for k, v in inputs.items()}
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "animalv2/fragments/studylevelvalue_row.html")
        assert resp.status_code == 200
        assert "System update" in str(resp.content)
        assert models.StudyLevelValue.objects.count() == initial_studylevelvalue_count + 1

        # studylevelvalues delete
        url = studylevelvalue.get_delete_url()
        resp = client.get(url)
        assert resp.status_code == 200
        assert "Are you sure you want to delete?" in str(resp.content)
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.StudyLevelValue.objects.count() == initial_studylevelvalue_count

    def test_permissions(self, db_keys):
        study_id = db_keys.study_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="reviewer@hawcproject.org", password="pw") is True

        initial_studylevelvalue_count = models.StudyLevelValue.objects.count()
        assert initial_studylevelvalue_count == 1

        url = reverse("animalv2:studylevelvalues-htmx", args=[study_id, "read"])
        resp = client.get(url)
        studylevelvalue = resp.context["object"]

        # studylevelvalues create
        url = reverse("animalv2:studylevelvalues-htmx", args=[study_id, "create"])
        inputs = {
            "studylevelvalue-new-system": "System name",
            "studylevelvalue-new-value_type": 1,
            "studylevelvalue-new-value": 10,
            "studylevelvalue-new-units": 1,
            "studylevelvalue-new-comments": "a comment",
        }
        resp = client.post(url, data=inputs)
        assert resp.status_code == 403
        assert initial_studylevelvalue_count == 1

        # studylevelvalues read
        url = studylevelvalue.get_absolute_url()
        resp = client.get(url)
        assertTemplateUsed(resp, "animalv2/fragments/studylevelvalue_row.html")
        assert resp.status_code == 200
        assert "Cardiovascular" in str(resp.content)

        # studylevelvalues update
        url = studylevelvalue.get_edit_url()
        inputs["studylevelvalue-new-system"] = "System update"
        resp = client.post(url, data=inputs)
        assert resp.status_code == 403

        # studylevelvalues delete
        url = studylevelvalue.get_delete_url()
        resp = client.get(url)
        assert resp.status_code == 403
        assert initial_studylevelvalue_count == 1


@pytest.mark.django_db
class TestExperimentChildren:
    def _test_helper(self, client, experiment, clazz, input_payload, short_name):
        initial_count = clazz.objects.count()
        name_val = input_payload[f"{short_name}-new-name"]
        expected_template = f"animalv2/fragments/_{short_name}_row.html"
        viewname = f"animalv2:{short_name}-htmx"

        # create
        url = reverse(viewname, args=(experiment.id, "create"))
        resp = client.post(url, data=input_payload)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val}</td>" in str(resp.content)
        created_obj = resp.context["object"]
        assert f"{short_name}-{created_obj.id}" in str(resp.content)
        assert clazz.objects.count() == initial_count + 1

        # clone
        url = reverse(viewname, args=(created_obj.id, "clone"))
        resp = client.post(url)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val} (2)</td>" in str(resp.content)
        assert clazz.objects.count() == initial_count + 2

        # read
        url = reverse(viewname, args=(created_obj.id, "read"))
        resp = client.get(url)
        assertTemplateUsed(resp, expected_template)
        assert resp.status_code == 200
        assert f"<td>{name_val}</td>" in str(resp.content)
        assert clazz.objects.count() == initial_count + 2

        # update
        url = reverse(viewname, args=(created_obj.id, "update"))
        input_payload[f"{short_name}-new-name"] = f"{name_val} update"
        input_payload = {k.replace("new", str(created_obj.id)): v for k, v in input_payload.items()}
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
            "chemical-new-name": "ex chemical",
            "chemical-new-namedtxsid": dsstox_id,
        }
        self._test_helper(client, experiment, models.Chemical, inputs, "chemical")

        # Animal Group
        strain = assessment_models.Strain.objects.first()
        species = assessment_models.Species.objects.get(pk=strain.species.id)
        inputs = {
            "animalgroup-new-name": "ex animalgroup",
            "animalgroup-new-species": species.id,
            "animalgroup-new-strain": strain.id,
            "animalgroup-new-sex": "M",
        }
        self._test_helper(client, experiment, models.AnimalGroup, inputs, "animalgroup")

        # TODO -- add sample payloads for all the other htmx forms...
