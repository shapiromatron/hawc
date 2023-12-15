import os

import pytest
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment
from hawc.apps.bmd.constants import BmdInputSettings, SelectedModel
from hawc.apps.bmd.models import Session

SKIP_BMDS_TESTS = bool(os.environ.get("SKIP_BMDS_TESTS", "False") == "True")
IN_CI = os.environ.get("GITHUB_RUN_ID") is not None


def toggle_assessment_lock(assessment_id: int, editable: bool):
    # lock/unlock assessment
    assess = Assessment.objects.get(id=assessment_id)
    assess.editable = editable
    assess.save()


@pytest.mark.django_db
class TestSessionViewSet:
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
        session = Session.objects.filter(version="BMDS330", active=True).first()
        url = session.get_execute_status_url()

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # check execute status on existing run
        resp = client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_finished"] is True
        assert data["date_executed"] is not None

        # create new run that hasn't been executed
        session2 = Session.create_new(endpoint=session.endpoint)
        url2 = session2.get_execute_status_url()
        resp = client.get(url2)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_finished"] is False
        assert data["date_executed"] is None

    @pytest.mark.skipif(SKIP_BMDS_TESTS or IN_CI, reason="BMDS execution environment unavailable")
    def test_write_operations(self):
        toggle_assessment_lock(2, True)

        session = Session.objects.filter(version="BMDS330", active=True).first()
        client = APIClient()

        # check permission
        url = session.get_api_url()
        resp = client.patch(url)
        assert resp.status_code == 403

        assert client.login(username="team@hawcproject.org", password="pw") is True

        # check invalid actions
        for data in [{}, {"action": "not-real"}]:
            resp = client.patch(url, data={}, format="json")
            assert resp.status_code == 200
            data = resp.json()
            assert data == {"status": "success", "id": 6}

        # check selected
        data_old = session.selected.copy()
        data_new = SelectedModel(
            model_index=1, model="Hill", bmr="1SD", notes="Hi", bmd=1
        ).model_dump(by_alias=True)
        assert data_old != data_new
        resp = client.patch(url, data={"action": "select", "selected": data_new}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"status": "success", "id": 6}

        # check bmd value has changed
        assert pytest.approx(12.7, abs=0.1) == session.selected["bmd"]
        session.refresh_from_db()
        assert session.selected == data_new
        session.selected = data_old
        session.save()

        # check execute
        data_old = session.inputs
        data_new = BmdInputSettings.create_default(session.endpoint).model_dump()
        data_new["bmr_value"] = 0.2
        assert data_old != data_new
        resp = client.patch(url, data={"action": "execute", "inputs": data_new}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"status": "success", "id": 6}

        toggle_assessment_lock(2, False)
