import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment import models
from hawc.apps.summary.models import Visual


@pytest.mark.django_db
class TestLabels:
    def test_labels(self, db_keys):
        assessment_id = db_keys.assessment_working
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        root_label = models.Label.get_assessment_root(db_keys.assessment_working)
        initial_label_count = models.Label.objects.count()

        # label create
        url = reverse("assessment:label-htmx", args=[assessment_id, "create"])
        inputs = {
            "label-new-name": "Label 2",
            "label-new-color": "#7cc587",
            "label-new-description": "Example label!",
            "label-new-parent": root_label.pk,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "assessment/fragments/label_row.html")
        assert resp.status_code == 200
        assert "Label 2" in str(resp.content)
        label = resp.context["object"]
        assert models.Label.objects.count() == initial_label_count + 1

        # label read
        url = label.get_absolute_url()
        resp = client.get(url)
        assertTemplateUsed(resp, "assessment/fragments/label_row.html")
        assert resp.status_code == 200
        assert "Label 2" in str(resp.content)

        # label update
        url = label.get_edit_url()
        inputs = {
            f"label-{label.pk}-name": "Label 2 Update!",
            f"label-{label.pk}-color": "#7cc587",
            f"label-{label.pk}-description": "Example label!",
            f"label-{label.pk}-parent": root_label.pk,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "assessment/fragments/label_row.html")
        assert resp.status_code == 200
        assert "Label 2 Update!" in str(resp.content)
        assert models.Label.objects.count() == initial_label_count + 1

        # label delete
        url = label.get_delete_url()
        resp = client.get(url)
        assert resp.status_code == 200
        assert "Are you sure you want to delete?" in str(resp.content)
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Label.objects.count() == initial_label_count


@pytest.mark.django_db
class TestLabeling:
    def test_labeling(self, db_keys):
        assessment_id = db_keys.assessment_working
        client = Client(headers={"hx-request": "true"})

        visual = Visual.objects.filter(assessment=assessment_id).first()
        content_type = ContentType.objects.get_for_model(Visual)
        base_url = reverse(
            "assessment:label-item",
            args=(content_type.pk, visual.pk),
        )

        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_labeled_items = models.LabeledItem.objects.count()
        label = models.Label.objects.filter(assessment=assessment_id)[1]

        # label
        url = f"{base_url}?action=label"
        data = {
            "labels": label.pk,
        }
        resp = client.post(url, data=data)
        assertTemplateUsed(resp, "assessment/components/label_modal_content.html")
        assert resp.status_code == 200
        assert "Apply labels" in str(resp.content)

        # label indicators
        url = f"{base_url}?action=label_indicators"
        resp = client.get(url)
        assertTemplateUsed(resp, "assessment/fragments/label_indicators.html")
        assert f"{label.name}" in str(resp.content)
        assert resp.status_code == 200

        assert models.LabeledItem.objects.count() == initial_labeled_items + 1
