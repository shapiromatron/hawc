import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animalv2 import models


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
