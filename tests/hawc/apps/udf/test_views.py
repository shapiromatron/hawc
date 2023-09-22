import pytest
from django.urls import reverse

from ..test_utils import check_200, check_403, check_status_code, get_client


@pytest.mark.django_db
class TestUDFViews:
    def test_permission(self, db_keys):
        # Login required (redirects to login)
        urls = [
            reverse("udf:udf_list"),
            reverse("udf:udf_create"),
        ]
        client = get_client()
        for url in urls:
            check_status_code(client, url, 302)

        # Permission denied
        urls = [
            reverse("udf:model_create", args=(db_keys.assessment_working,)),
            reverse("udf:tag_create", args=(db_keys.assessment_working,)),
        ]
        client = get_client()
        for url in urls:
            check_403(client, url)

    def test_success(self, db_keys):
        urls = [
            reverse("udf:udf_list"),
            reverse("udf:udf_create"),
            reverse("udf:model_create", args=(db_keys.assessment_working,)),
            reverse("udf:tag_create", args=(db_keys.assessment_working,)),
        ]
        client = get_client("pm")
        for url in urls:
            check_200(client, url)
