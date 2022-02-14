import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAdminDashboardViewset:
    def test_permissions(self):
        client = APIClient()

        # failure - not admin
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-media")
        resp = client.get(url)
        assert resp.status_code == 403

        # success - admin
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-media")
        resp = client.get(url)
        assert resp.status_code == 200

    def test_media_report(self, media_file):
        client = APIClient()
        # check that media report successfully returns a csv header
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("assessment:api:admin_dashboard-media") + "?format=csv"
        resp = client.get(url)
        assert resp.status_code == 200
        header = resp.content.decode().split("\n")[0]
        assert header == "name,extension,full_path,hash,uri,media_preview,size_mb,created,modified"
