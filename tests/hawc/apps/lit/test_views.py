import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateNotUsed, assertTemplateUsed


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
