import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_smoke_get():
    client = get_client("pm")
    urls = [
        reverse("vocab:ehv-browse", args=()),
    ]
    for url in urls:
        check_200(client, url)
