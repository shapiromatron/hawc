import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.lit import models


@pytest.mark.django_db
class TestWorkflows:
    def test_workflows(self, db_keys):
        assessment_id = db_keys.assessment_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_workflow_count = models.Workflow.objects.count()
        tags = models.ReferenceFilterTag.get_assessment_qs(assessment_id)

        # workflow create
        url = reverse("lit:workflow-create", args=[assessment_id])
        inputs = {
            "title": "Title/Abstract",
            "description": "Example title/abstract workflow",
            "admission_tags": tags.all()[0].id,
            "admission_tags_descendants": True,
            "completion_tags": tags.all()[1].id,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "lit/fragments/workflow_row.html")
        assert resp.status_code == 200
        assert "Title/Abstract" in str(resp.content)
        workflow = resp.context["object"]
        assert models.Workflow.objects.count() == initial_workflow_count + 1

        # workflow read
        url = reverse("lit:workflow-detail", args=[workflow.id])
        resp = client.get(url)
        assertTemplateUsed(resp, "lit/fragments/workflow_row.html")
        assert resp.status_code == 200
        assert "Title/Abstract" in str(resp.content)

        # workflow update
        url = reverse("lit:workflow-update", args=[workflow.id])
        inputs = {
            "title": "Title/Abstract update",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "lit/fragments/workflow_row.html")
        assert resp.status_code == 200
        assert "Title/Abstract update" in str(resp.content)
        assert models.Workflow.objects.count() == initial_workflow_count + 1

        # workflow delete
        url = reverse("lit:workflow-delete", args=[workflow.id])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Workflow.objects.count() == initial_workflow_count
