import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    main = 1
    urls = [
        reverse("vocab:ehv-browse"),
        reverse("vocab:toxrefdb-browse"),
        reverse("vocab:observation-list", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestObservationViewSet:
    def test_crud(self):
        c = Client(HTTP_HX_REQUEST="true")
        assert c.login(username="admin@hawcproject.org", password="pw") is True

        # create (post)
        url = (
            reverse("vocab:observation-htmx", args=(1, "tested_status", "create"))
            + "?endpoint=7002"
        )
        response = c.post(
            url,
            {
                "7002-tested": "True",
            },
            follow=True,
        )
        assertTemplateUsed("vocab/fragments/observation_form.html")
        assert response.status_code == 200
