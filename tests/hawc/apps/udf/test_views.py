import pytest
from django.urls import reverse

from ..test_utils import check_200, check_302, check_403, get_client


@pytest.mark.django_db
class TestUDFViews:
    def test_permissions(self, db_keys):
        urls = [
            # TODO - add more
            # udf
            ("login", reverse("udf:udf_list")),
            ("owner", reverse("udf:udf_update", args=(1,))),
            ("read", reverse("udf:binding-list", args=(db_keys.assessment_conflict_resolution,))),
        ]
        anon = get_client()
        reviewer = get_client("reviewer")
        team = get_client("team")
        for role, url in urls:
            if role == "login":
                # login required
                check_302(anon, url, reverse("user:login"))
                check_200(reviewer, url)
            elif role == "owner":
                # UDF owner/editor required
                check_403(reviewer, url)
                check_200(team, url)
            elif role == "read":
                # read-only required
                check_403(anon, url)
                check_200(reviewer, url)
            elif role == "update":
                # team-member or higher
                check_403(reviewer, url)
                check_200(team, url)
            else:
                raise ValueError("Unknown role.")
