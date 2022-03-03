from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.common.diagnostics import worker_healthcheck


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


@pytest.fixture(scope="module")
def media_file():
    fn = Path(settings.MEDIA_ROOT) / "test.txt"
    if not fn.exists():
        fn.write_text("hello\n")


@pytest.mark.django_db
class TestAdminDashboardViewset:
    def test_permissions(self):
        client = APIClient()

        # failure - not admin
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        url = reverse("api:admin_dashboard-media")
        resp = client.get(url)
        assert resp.status_code == 403

        # success - admin
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("api:admin_dashboard-media")
        resp = client.get(url)
        assert resp.status_code == 200

    def test_media_report(self, media_file):
        client = APIClient()
        # check that media report successfully returns a csv header
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("api:admin_dashboard-media") + "?format=csv"
        resp = client.get(url)
        assert resp.status_code == 200
        header = resp.content.decode().split("\n")[0]
        assert header == "name,extension,full_path,hash,uri,media_preview,size_mb,created,modified"


@pytest.mark.django_db
class TestHealthcheckViewset:
    def test_web(self):
        client = APIClient()
        url = reverse("api:healthcheck-web")
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json() == {"healthy": True}

    @pytest.mark.skipif(not has_redis(), reason="skip; redis cache required")
    def test_worker(self):
        client = APIClient()
        url = reverse("api:healthcheck-worker")

        # no data; should be an error
        resp = client.get(url)
        assert resp.status_code == 400
        assert resp.json()["healthy"] is False

        # has recent data; should be healthy
        worker_healthcheck.push()
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["healthy"] is True

    @pytest.mark.skipif(not has_redis(), reason="skip; redis cache required")
    def test_worker_plot(self):
        client = APIClient()
        url = reverse("api:healthcheck-worker-plot")

        # failure - not admin
        resp = client.get(url)
        assert resp.status_code == 403
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 403

        # success - admin
        assert client.login(username="admin@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200
