import pytest
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment
from hawc.apps.bmd.models import Session


@pytest.mark.django_db(transaction=True)
class TestSessionViewset:
    def test_selected_model(self):
        assess_id = 2
        Assessment.objects.filter(id=assess_id).update(editable=True)

        anon_client = APIClient()
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # setup - make assessment editable; fetch required metadata
        session = Session.objects.filter(endpoint__assessment=assess_id).first()
        model = session.models.first()
        url = session.get_selected_model_url()

        payload = {"model": model.id, "notes": "example notes"}

        # anon forbidden
        resp = anon_client.post(url, payload, format="json")
        assert resp.status_code == 403

        # team member, with model
        resp = client.post(url, payload, format="json")
        assert resp.status_code == 200

        # team member, no model
        payload["model"] = None
        resp = client.post(url, payload, format="json")
        assert resp.status_code == 200
