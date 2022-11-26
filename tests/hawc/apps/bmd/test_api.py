import pytest
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment
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

    def test_bmds3_detail(self):
        # bmds 330
        # TODO - BMDS3 - reimplement after integration
        ...

    def test_execute(self):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        # TODO - BMDS3 - reimplement after integration

    def test_selected_model(self):
        assess_id = 2
        Assessment.objects.filter(id=assess_id).update(editable=True)

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # TODO - BMDS3 - reimplement after integration
