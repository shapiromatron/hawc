import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_smoke_get():
    client = get_client("pm")
    main = 1
    urls = [
        # modify settings
        reverse("riskofbias:arob_detail", args=(main,)),
        reverse("riskofbias:arob_copy", args=(main,)),
        reverse("riskofbias:arob_load_approach", args=(main,)),
        reverse("riskofbias:arob_update", args=(main,)),
        reverse("riskofbias:arob_text_update", args=(main,)),
        # modify domains
        reverse("riskofbias:robd_create", args=(main,)),
        reverse("riskofbias:robd_update", args=(main,)),
        reverse("riskofbias:robd_delete", args=(main,)),
        # modify metrics
        reverse("riskofbias:robm_create", args=(main,)),
        reverse("riskofbias:robm_update", args=(main,)),
        reverse("riskofbias:robm_delete", args=(main,)),
        # reviewers
        reverse("riskofbias:rob_assignments", args=(main,)),
        reverse("riskofbias:rob_assignments_update", args=(main,)),
        reverse("riskofbias:rob_num_reviewers", args=(main,)),
        # study level
        reverse("riskofbias:rob_detail", args=(main,)),
        reverse("riskofbias:rob_detail_all", args=(main,)),
        # editing views
        reverse("riskofbias:rob_update", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)
