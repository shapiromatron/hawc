import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_smoke_get():
    client = get_client("admin")
    main = 1
    urls = [
        reverse("meta:protocol_create", args=(main,)),
        reverse("meta:protocol_detail", args=(main,)),
        reverse("meta:protocol_update", args=(main,)),
        reverse("meta:protocol_delete", args=(main,)),
        reverse("meta:result_list", args=(main,)),
        reverse("meta:result_create", args=(main,)),
        reverse("meta:result_copy_selector", args=(main,)),
        reverse("meta:result_detail", args=(main,)),
        reverse("meta:result_update", args=(main,)),
        reverse("meta:result_delete", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)
