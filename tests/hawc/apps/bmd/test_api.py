from io import BytesIO

import pytest
from docx import Document

from hawc.apps.bmd.constants import BmdInputSettings, SelectedModel
from hawc.apps.bmd.models import Session

from ..test_utils import get_client


@pytest.mark.django_db
class TestSessionViewSet:
    def test_bmds2(self):
        session = Session.objects.filter(version="BMDS270", active=True).first()
        url = session.get_api_url()

        client = get_client("team", api=True)

        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        assert data["inputs"]["version"] == 1
        assert data["selected"]["version"] == 1

    def test_bmds24_1_detail(self):
        session = Session.objects.filter(version="24.1", active=True).first()
        url = session.get_api_url()

        client = get_client("team", api=True)

        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        assert data["inputs"]["version"] == 2
        assert data["selected"]["version"] == 2

    def test_execute_status(self):
        session = Session.objects.filter(version="24.1", active=True).first()
        url = session.get_execute_status_url()

        client = get_client("team", api=True)

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

    def test_write_operations(self):
        session = Session.objects.filter(version="24.1", active=True).first()
        client = get_client("", api=True)

        # check permission
        url = session.get_api_url()
        resp = client.patch(url)
        assert resp.status_code == 403

        team_client = get_client("team", api=True)

        # check invalid actions
        for data in [{}, {"action": "not-real"}]:
            resp = team_client.patch(url, data={}, format="json")
            assert resp.status_code == 200
            data = resp.json()
            assert data == {"status": "success", "id": 7}

        # check selected
        selected_old = session.selected.copy()
        selected_new = SelectedModel(
            model_index=1, model="Hill", bmr="1SD", notes="Hi", bmd=1
        ).model_dump(by_alias=True)
        assert selected_old != selected_new
        resp = team_client.patch(
            url, data={"action": "select", "selected": selected_new}, format="json"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"status": "success", "id": 7}

        session.refresh_from_db()
        assert session.selected == selected_new
        session.selected = selected_old
        session.save()

        # check execute
        data_old = session.inputs
        data_new = BmdInputSettings.create_default(session.endpoint).model_dump()
        data_new["bmr_value"] = 0.2
        assert data_old != data_new
        resp = team_client.patch(url, data={"action": "execute", "inputs": data_new}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"status": "success", "id": 7}

    def test_report(self):
        client = get_client("team", api=True)

        session = Session.objects.filter(version="24.1", active=True).first()
        url = session.get_report_url()
        resp = client.get(url)
        assert resp.status_code == 200
        docx = Document(BytesIO(resp.content))
        assert len(docx.paragraphs) > 0
