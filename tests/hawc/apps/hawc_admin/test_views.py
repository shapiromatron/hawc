import pytest
from django.http.response import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from wagtail.admin.views.account import BaseSettingsPanel, NameEmailSettingsPanel, account

from hawc.apps.myuser.models import HAWCUser

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
        actions = [
            "assessment_size",
            "assessment_growth",
            "assessment_profile",
            "growth",
            "users",
            "daily_changes",
        ]
        for action in actions:
            url = reverse("admin_dashboard") + f"?action={action}"
            resp = pm_client.get(url)
            check_admin_login_redirect(resp)
            resp = admin_client.get(url)
            assert resp.status_code == 200

    def test_htmx_form_get(self):
        admin_client = get_client("admin")
        requests = [
            ("?action=growth", {"assessment_id": 1, "grouper": "W"}),
            ("?action=assessment_profile", {"model": "assessment", "grouper": "year"}),
        ]
        for extra, data in requests:
            url = reverse("admin_dashboard") + extra
            resp = admin_client.get(url)
            assert resp.status_code == 200
            resp = admin_client.get(url, data=data)
            assert resp.status_code == 200


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


@pytest.mark.django_db
class TestWagtailAccounts:
    def test_no_name_email_panel(self):
        # confirm `NameEmailSettingsPanel` is removed from the accounts page
        factory = RequestFactory()
        request = factory.get("/admin/cms/account/")
        request.user = HAWCUser.objects.filter(is_superuser=True).first()
        response = account(request)
        for panel_set in response.context_data["panels_by_tab"].values():
            for panel in panel_set:
                assert isinstance(panel, BaseSettingsPanel)
                assert not isinstance(panel, NameEmailSettingsPanel)
