import pytest
from django.http.response import HttpResponse
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ..test_utils import check_200, get_client


def check_admin_login_redirect(resp: HttpResponse):
    assert resp.status_code == 302
    assert resp.url.startswith("/admin/login/")


@pytest.mark.django_db
class TestSwagger:
    def test_permission(self):
        url = reverse("swagger")
        client = get_client("pm")
        resp = client.get(url)
        check_admin_login_redirect(resp)

    def test_success(self, db_keys):
        url = reverse("swagger")
        client = get_client("admin")
        resp = check_200(client, url)
        assertTemplateUsed(resp, "admin/swagger.html")


@pytest.mark.django_db
class TestDashboard:
    def test_index(self):
        url = reverse("admin_dashboard")
        # invalid
        client = get_client("pm")
        resp = client.get(url)
        check_admin_login_redirect(resp)
        # valid
        client = get_client("admin")
        resp = check_200(client, url)
        assertTemplateUsed(resp, "admin/dashboard.html")

    def test_htmx_get(self):
        pm_client = get_client("pm")
        admin_client = get_client("admin")
        urls = [
            "admin_dashboard_growth",
            "admin_dashboard_users",
            "admin_dashboard_assessments",
            "admin_dashboard_assessment_profile",
            "admin_dashboard_assessment_size",
            "admin_dashboard_changes",
        ]
        for url in urls:
            resp = pm_client.get(reverse(url))
            check_admin_login_redirect(resp)
            resp = admin_client.get(reverse(url))
            assert resp.status_code == 400
            resp = admin_client.get(reverse(url), HTTP_HX_REQUEST="true")
            assert resp.status_code == 200

    def test_htmx_post(self):
        admin_client = get_client("admin")
        requests = [
            ("admin_dashboard_growth", {"assessment_id": 1, "grouper": "W"}),
            ("admin_dashboard_assessment_profile", {"model": "assessment", "grouper": "year"}),
        ]
        for url, data in requests:
            resp = admin_client.get(reverse(url), HTTP_HX_REQUEST="true")
            assert resp.status_code == 200
            resp = admin_client.post(reverse(url), data=data, HTTP_HX_REQUEST="true")
            assert resp.status_code == 200


@pytest.mark.django_db
@pytest.mark.django_db
class TestMediaPreview:
    def test_permission(self):
        url = reverse("admin_media_preview")
        client = get_client("pm")
        resp = client.get(url)
        check_admin_login_redirect(resp)

    def test_success(self, db_keys):
        url = reverse("admin_media_preview")
        client = get_client("admin")
        resp = check_200(client, url)
        assertTemplateUsed(resp, "admin/media_preview.html")
