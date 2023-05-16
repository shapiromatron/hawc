from io import BytesIO

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateNotUsed, assertTemplateUsed

from hawc.apps.lit.models import Reference
from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestViewPermissions:
    def test_success(self, db_keys):
        clients = ["admin@hawcproject.org", "pm@hawcproject.org", "team@hawcproject.org"]
        views = [
            reverse("lit:tag-status", args=(3,)),
            reverse("lit:tag-conflicts", args=(db_keys.assessment_working,)),
        ]
        for client in clients:
            c = Client()
            assert c.login(username=client, password="pw") is True
            for view in views:
                response = c.get(view)
                assert response.status_code == 200

    def test_failure(self, db_keys):
        # anonymous user
        c = Client()
        views = [
            (reverse("lit:tag-status", args=(3,)), 403),
            (reverse("lit:tag-conflicts", args=(db_keys.assessment_working,)), 403),
        ]
        for url, status in views:
            response = c.get(url)
            assert response.status_code == status


@pytest.mark.django_db
def test_reference_delete(db_keys):
    c = Client()
    assert c.login(username="pm@hawcproject.org", password="pw") is True

    # Case 1 - reference has no study; should be able to delete
    url = reverse("lit:ref_delete", args=(3,))

    # get should show delete button
    with assertTemplateUsed("hawc/_delete_block.html"):
        resp = c.get(url)
    assert resp.status_code == 200

    # delete verb not used
    resp = c.delete(url)
    assert resp.status_code == 405

    # delete works
    resp = c.post(url)
    assert resp.status_code == 302
    assert resp.url == reverse("lit:overview", args=(1,))

    # get should not show delete button
    url = reverse("lit:ref_delete", args=(1,))
    with assertTemplateNotUsed("hawc/_delete_block.html"):
        resp = c.get(url)
    assert resp.status_code == 200

    # delete fails
    resp = c.post(url)
    assert resp.status_code == 403


@pytest.mark.django_db
class TestRefUploadExcel:
    def test_success(self):
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        # check GET renders
        url = reverse("lit:ref_upload", args=(1,))
        resp = c.get(url)
        assertTemplateUsed(resp, "lit/reference_upload_excel.html")

        ref = Reference.objects.get(id=1)
        assert ref.full_text_url == ""

        # check POST works
        df = pd.DataFrame(
            data={
                "HAWC ID": [1],
                "Full text URL": ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5448372/"],
            }
        )
        f = BytesIO()
        df.to_excel(f, index=False)
        resp = c.post(
            url, {"excel_file": SimpleUploadedFile("test.xlsx", f.getvalue())}, follow=True
        )
        assertTemplateUsed(resp, "lit/overview.html")

        ref.refresh_from_db()
        assert ref.full_text_url.startswith("https://www.ncbi.nlm.nih.gov")


@pytest.mark.django_db
class TestRefListExtract:
    def test_success(self):
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        success = b"Selected references were successfully converted to studies"

        qs = Study.objects.filter(id=11)
        assert qs.exists() is False

        # check GET renders
        url = reverse("lit:ref_list_extract", args=(4,))
        with assertTemplateUsed("lit/reference_extract_list.html"):
            resp = c.get(url)
        assert success not in resp.content

        # check POST works
        resp = c.post(url, {"references": 11, "study_type": "bioassay"}, follow=True)
        assert success in resp.content
        assert qs.exists() is True
