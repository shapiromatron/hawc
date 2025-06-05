import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    urls = [
        reverse("vocab:ehv-browse"),
        reverse("vocab:toxrefdb-browse"),
    ]
    for url in urls:
        check_200(client, url)
