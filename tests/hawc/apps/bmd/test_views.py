import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_smoke_get():
    client = get_client("admin")
    main = 1
    sessions = 5

    url = reverse("bmd:session_create", args=(3,))
    assert client.get(url).status_code == 302

    urls = [
        reverse("bmd:assess_settings_detail", args=(main,)),
        reverse("bmd:assess_settings_update", args=(main,)),
        reverse("bmd:session_list", args=(main,)),
        reverse("bmd:session_detail", args=(sessions,)),
        reverse("bmd:session_update", args=(sessions,)),
        reverse("bmd:session_delete", args=(sessions,)),
    ]
    for url in urls:
        check_200(client, url)
