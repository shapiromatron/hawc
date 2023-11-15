import pytest
from django.urls import reverse

from ..test_utils import check_200, check_302, check_403, get_client


@pytest.mark.django_db
class TestDocsViews:
    def test_permissions(self, db_keys):
        urls = [
            ("login", reverse("wagtail_serve", args=("",))),
            ("login", reverse("wagtaildocs_serve", args=("",))),
            ("admin", reverse("wagtailadmin_home")),
        ]
        anon = get_client()
        reviewer = get_client("reviewer")
        admin = get_client("admin")
        for role, url in urls:
            if role == "login":
                # login required
                check_302(anon, url, reverse("user:login"))
                check_200(reviewer, url)
            elif role == "admin":
                # admin required
                check_302(reviewer, url, reverse("wagtailadmin_login"))
                check_200(admin, url)

            else:
                raise ValueError("Unknown role.")
