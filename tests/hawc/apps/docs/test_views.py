import pytest
from django.urls import reverse

from hawc.apps.docs import models

from ..test_utils import check_200, check_302, check_404, get_client


@pytest.mark.django_db
class TestDocsViews:
    def test_permissions(self, db_keys):
        draft = models.DocsPage.objects.get(title="Draft Page")
        public = models.DocsPage.objects.get(title="Public Page")

        urls = [
            ("login", reverse("wagtail_serve", args=("",))),
            ("login", public.get_url()),
            ("404", draft.get_url()),
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
            elif role == "404":
                # always returns 404 (not published yet)
                check_404(admin, url)

            else:
                raise ValueError("Unknown role.")
