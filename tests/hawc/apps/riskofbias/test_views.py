import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client

@pytest.mark.django_db
def test_smoke_get():
    client = get_client("pm")

    urls = [
        # modify settings
        reverse("riskofbias:arob_detail", args=(1,)),
        reverse("riskofbias:arob_copy", args=(1,)),
        reverse("riskofbias:arob_load_approach", args=(1,)),
        reverse("riskofbias:arob_update", args=(1,)),
        reverse("riskofbias:arob_text_update", args=(1,)),
        # modify domains
        reverse("riskofbias:robd_create", args=(1,)),
        reverse("riskofbias:robd_update", args=(1,)),
        reverse("riskofbias:robd_delete", args=(1,)),
        # modify metrics
        reverse("riskofbias:robm_create", args=(1,)),
        reverse("riskofbias:robm_update", args=(1,)),
        reverse("riskofbias:robm_delete", args=(1,)),
        # reviewers
        reverse("riskofbias:rob_assignments", args=(1,)),
        reverse("riskofbias:rob_assignments_update", args=(1,)),
        reverse("riskofbias:rob_num_reviewers", args=(1,)),
        # study level
        reverse("riskofbias:rob_detail", args=(1,)),
        reverse("riskofbias:rob_detail_all", args=(1,)),
        # editing views
        reverse("riskofbias:rob_update", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)
