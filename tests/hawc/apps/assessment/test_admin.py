import pytest
from django.urls import reverse

from ..test_utils import get_client


@pytest.mark.django_db
class TestDSSXToxAdmin:
    def test_list(self):
        client = get_client("admin")
        url = reverse("admin:assessment_dsstox_changelist")
        resp = client.get(url)
        assert resp.status_code == 200
