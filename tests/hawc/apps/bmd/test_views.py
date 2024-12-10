import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("admin")
    endpoint_id = 12
    session_id = 6

    url = reverse("bmd:session_create", args=(endpoint_id,))
    assert client.get(url).status_code == 302

    urls = [
        reverse("bmd:session_list", args=(endpoint_id,)),
        reverse("bmd:session_detail", args=(session_id,)),
        reverse("bmd:session_update", args=(session_id,)),
        reverse("bmd:session_delete", args=(session_id,)),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestSesssionCreate:
    def test_bad_request(self):
        client = get_client("")
        url = reverse("bmd:session_create", args=(12,))
        resp = client.get(url)
        assert resp.status_code == 403


@pytest.mark.django_db
def test_bmds2_views():
    client = get_client("admin")

    # check _get_session_config works for bmds2
    url = reverse("bmd:session_detail", args=(2,))
    check_200(client, url)

    # check update throws a bad request
    url = reverse("bmd:session_update", args=(2,))
    resp = client.get(url)
    assert resp.status_code == 400
