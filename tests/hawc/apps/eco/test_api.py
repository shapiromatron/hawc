import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.common.helper import FlatExport


@pytest.mark.django_db
class TestAssessmentViewSet:
    def test_nested(self):
        client = APIClient()
        url = reverse("eco:api:assessment-export", args=(1,))

        # check permissions; must be authenticated
        assert client.get(url).status_code == 403

        # check successful status code
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # check successful response data shape
        assert isinstance(resp.data, FlatExport)
        assert resp.data.df.shape == (1, 81)
        assert "study-id" in resp.data.df.columns


@pytest.mark.django_db
class TestTermViewSet:
    def test_nested(self):
        client = APIClient()
        url = reverse("eco:api:terms-nested")

        # check permissions; must be authenticated
        assert client.get(url).status_code == 403

        # check successful status code
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        # check successful response data shape
        assert isinstance(resp.data, FlatExport)
        assert resp.data.df.shape == (1, 3)
        assert resp.data.df.columns.tolist() == ["ID", "Depth", "Level 1"]
