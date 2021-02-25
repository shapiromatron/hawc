import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertTemplateNotUsed


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

    # delete works
    resp = c.delete(url)
    assert resp.status_code == 302
    assert resp.url == reverse("lit:overview", args=(1,))

    # get should not show delete button
    url = reverse("lit:ref_delete", args=(1,))
    with assertTemplateNotUsed("hawc/_delete_block.html"):
        resp = c.get(url)
    assert resp.status_code == 200

    # delete fails
    resp = c.delete(url)
    assert resp.status_code == 403
