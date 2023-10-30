import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    urls = [
        reverse("animal:experiment_new", args=(1,)),
        reverse("animal:experiment_copy", args=(1,)),
        reverse("animal:experiment_detail", args=(1,)),
        reverse("animal:experiment_update", args=(1,)),
        reverse("animal:experiment_delete", args=(1,)),
        reverse("animal:animal_group_new", args=(1,)),
        reverse("animal:animal_group_copy", args=(1,)),
        reverse("animal:animal_group_detail", args=(1,)),
        reverse("animal:animal_group_update", args=(1,)),
        reverse("animal:animal_group_delete", args=(1,)),
        reverse("animal:endpoint_copy", args=(1,)),
        reverse("animal:dosing_regime_update", args=(1,)),
        reverse("animal:endpoint_list", args=(1,)),
        reverse("animal:endpoint_new", args=(1,)),
        reverse("animal:endpoint_detail", args=(1,)),
        reverse("animal:endpoint_update", args=(1,)),
        reverse("animal:endpoint_delete", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)
