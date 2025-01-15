import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.lit.models import ReferenceFilterTag
from hawc.apps.udf import constants, models


@pytest.mark.django_db
class TestBindings:
    def test_tagbindings(self, db_keys):
        assessment_id = db_keys.assessment_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_tagbinding_count = models.TagBinding.objects.count()

        udf_id = models.UserDefinedForm.objects.first().id
        tags = ReferenceFilterTag.get_assessment_qs(assessment_id)

        # tag binding create
        url = reverse("udf:binding_create", args=[assessment_id, constants.BindingType.TAG.value])
        inputs = {
            "tag-new-form": udf_id,
            "tag-new-tag": tags[1].id,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert tags[1].name in str(resp.content)
        tag_binding = resp.context["binding"]
        assert models.TagBinding.objects.count() == initial_tagbinding_count + 1

        # tag binding read
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.TAG.value, tag_binding.id, "read"]
        )
        resp = client.get(url)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert "tag" in str(resp.content)

        # tag binding update
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.TAG.value, tag_binding.id, "update"]
        )
        inputs = {
            f"tag-{tag_binding.id}-form": udf_id,
            f"tag-{tag_binding.id}-tag": tags[2].id,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert tags[2].name in str(resp.content)
        assert models.TagBinding.objects.count() == initial_tagbinding_count + 1

        # tag binding delete
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.TAG.value, tag_binding.id, "delete"]
        )
        resp = client.get(url)
        assert resp.status_code == 200
        assert "Are you sure you want to delete?" in str(resp.content)
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.TagBinding.objects.count() == initial_tagbinding_count

    def test_modelbindings(self, db_keys):
        assessment_id = db_keys.assessment_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_modelbinding_count = models.ModelBinding.objects.count()

        udf_id = models.UserDefinedForm.objects.first().id

        # model binding create
        url = reverse("udf:binding_create", args=[assessment_id, constants.BindingType.MODEL.value])
        inputs = {
            "model-new-form": udf_id,
            "model-new-content_type": 87,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert "Study" in str(resp.content)
        model_binding = resp.context["binding"]
        assert models.ModelBinding.objects.count() == initial_modelbinding_count + 1

        # model binding read
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.MODEL.value, model_binding.id, "read"]
        )
        resp = client.get(url)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert "Study" in str(resp.content)

        # model binding update
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.MODEL.value, model_binding.id, "update"]
        )
        inputs = {
            f"model-{model_binding.id}-form": udf_id,
            f"model-{model_binding.id}-content_type": 91,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "udf/fragments/udf_row.html")
        assert resp.status_code == 200
        assert "endpoint" in str(resp.content)
        assert models.ModelBinding.objects.count() == initial_modelbinding_count + 1

        # model binding delete
        url = reverse(
            "udf:binding_htmx", args=[constants.BindingType.MODEL.value, model_binding.id, "delete"]
        )
        resp = client.get(url)
        assert resp.status_code == 200
        assert "Are you sure you want to delete?" in str(resp.content)
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.ModelBinding.objects.count() == initial_modelbinding_count
