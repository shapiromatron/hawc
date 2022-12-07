import pytest
from rest_framework.test import APIClient

from hawc.apps.bmd.models import Session


@pytest.mark.django_db
class TestSessionViewset:
    def test_bmds2_detail(self):
        # bmds 270
        session = Session.objects.filter(version="BMDS270", active=True).first()
        url = session.get_api_url()

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        assert data["inputs"]["version"] == 1
        assert data["selected"]["version"] == 1

    def test_bmds3_detail(self):
        # bmds 330
        session = Session.objects.filter(version="BMDS330", active=True).first()
        url = session.get_api_url()

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        assert data["inputs"]["version"] == 2
        assert data["selected"]["version"] == 2

    def test_execute_status(self):
        assert "up" == "down"

    def test_post(self):
        # noop
        # invalid action
        # execute
        # selected
        # http://127.0.0.1:8000/bmd/api/session/5/
        # http://127.0.0.1:8000/bmd/api/session/5/execute-status/
        assert "up" == "down"
