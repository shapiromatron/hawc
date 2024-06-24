from io import BytesIO

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateNotUsed, assertTemplateUsed

from hawc.apps.lit.models import Reference, ReferenceFilterTag
from hawc.apps.study.models import Study

from ..test_utils import check_200, get_client


@pytest.mark.django_db
class TestViewPermissions:
    def test_success(self, db_keys):
        clients = ["admin@hawcproject.org", "pm@hawcproject.org", "team@hawcproject.org"]
        views = [
            reverse("lit:tag-status", args=(3,)),
            reverse("lit:tag-conflicts", args=(db_keys.assessment_working,)),
            reverse("lit:workflows", args=(db_keys.assessment_working,)),
            reverse("lit:overview", args=(db_keys.assessment_conflict_resolution,)),
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
            (reverse("lit:workflows", args=(db_keys.assessment_working,)), 403),
            (reverse("lit:overview", args=(db_keys.assessment_conflict_resolution,)), 403),
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


@pytest.mark.django_db
class TestRefFilterList:
    def test_full_text_search(self, db_keys):
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        url = reverse("lit:ref_search", args=(db_keys.assessment_final,))

        # search by author/year combo
        resp = c.get(url + "?ref_search=kawana+2001")
        n_results = b"References (1 found)"
        title = b"Psycho-physiological effects of the terrorist sarin attack on the Tokyo subway system."
        assert (n_results in resp.content) and (title in resp.content)


@pytest.mark.django_db
class TestTagsCopy:
    def test_success(self):
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        a_id = 3

        # check GET
        url = reverse("lit:tags_copy", args=(a_id,))
        resp = c.get(url)
        assertTemplateUsed(resp, "lit/tags_copy.html")

        assert not ReferenceFilterTag.get_assessment_qs(a_id).filter(name="Tier III Demo").exists()

        # check POST
        resp = c.post(url, {"assessment": 4, "confirmation": "confirm"}, follow=True)
        assertTemplateUsed(resp, "lit/tags_update.html")

        assert ReferenceFilterTag.get_assessment_qs(a_id).filter(name="Tier III Demo").exists()


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    main = 1
    slug_search = "manual-import"

    urls = [
        reverse("lit:overview", args=(main,)),
        # crud tags
        reverse("lit:tags_update", args=(main,)),
        reverse("lit:literature_assessment_update", args=(main,)),
        # reference-level details
        reverse("lit:ref_detail", args=(main,)),
        reverse("lit:ref_edit", args=(main,)),
        reverse("lit:ref_delete", args=(main,)),
        reverse("lit:tag-status", args=(main,)),
        reverse("lit:tag", args=(main,)),
        reverse("lit:bulk_tag", args=(main,)),
        reverse("lit:ref_list", args=(main,)),
        reverse("lit:ref_list_extract", args=(main,)),
        reverse("lit:ref_visual", args=(main,)),
        reverse("lit:ref_search", args=(main,)),
        reverse("lit:ref_upload", args=(main,)),
        # crud searches
        reverse("lit:search_new", args=(main,)),
        reverse("lit:copy_search", args=(main,)),
        reverse("lit:search_detail", args=(main, slug_search)),
        reverse("lit:search_update", args=(main, slug_search)),
        reverse("lit:search_delete", args=(main, slug_search)),
        # crud import
        reverse("lit:import_new", args=(main,)),
        reverse("lit:import_ris_new", args=(main,)),
        # edit tags
        reverse("lit:search_tags", args=(main, slug_search)),
        reverse("lit:search_tags_visual", args=(main, slug_search)),
        reverse("lit:ris_export_instructions"),
        reverse("lit:tag-conflicts", args=(main,)),
        reverse("lit:user-tag-list", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)
