import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200(db_keys):
    client = get_client("admin")
    main = db_keys.assessment_working
    endpoint_assessment = 5
    urls = [
        reverse("invitro:experiment_create", args=(main,)),
        reverse("invitro:experiment_detail", args=(main,)),
        reverse("invitro:experiment_update", args=(main,)),
        reverse("invitro:experiment_delete", args=(main,)),
        reverse("invitro:chemical_create", args=(main,)),
        reverse("invitro:chemical_detail", args=(main,)),
        reverse("invitro:chemical_update", args=(main,)),
        reverse("invitro:chemical_delete", args=(main,)),
        reverse("invitro:celltype_create", args=(main,)),
        reverse("invitro:celltype_detail", args=(main,)),
        reverse("invitro:celltype_update", args=(main,)),
        reverse("invitro:celltype_delete", args=(main,)),
        reverse("invitro:endpointcategory_update", args=(main,)),
        reverse("invitro:endpoint_list", args=(main,)),
        reverse("invitro:endpoint_create", args=(main,)),
        reverse("invitro:endpoint_detail", args=(endpoint_assessment,)),
        reverse("invitro:endpoint_update", args=(endpoint_assessment,)),
        reverse("invitro:endpoint_delete", args=(endpoint_assessment,)),
    ]
    for url in urls:
        check_200(client, url)
