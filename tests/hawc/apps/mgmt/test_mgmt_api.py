import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestTaskViewset:
    def test_permissions(self):
        url = reverse("mgmt:api:task-detail", args=(1,))

        for username, status_code in [
            ("pm@hawcproject.org", 200),
            ("team@hawcproject.org", 200),
            ("reviewer@hawcproject.org", 200),
            (None, 403),
        ]:
            client = APIClient()
            if username:
                assert client.login(username=username, password="pw") is True
            assert client.get(url).status_code == status_code

    def test_task_patch(self):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        url = reverse("mgmt:api:task-detail", args=(1,))

        # check initial data
        resp = client.get(url).json()
        assert resp["id"] == 1
        assert resp["status"] == 30
        assert resp["owner"]["id"] == 3

        # check changing status
        resp = client.patch(url, {"status": 40}, format="json").json()
        assert resp["status"] == 40

        # check changing owner to None
        resp = client.patch(url, {"owner": None}, format="json").json()
        assert resp["owner"] is None

        # check changing owner an owner
        resp = client.patch(url, {"owner": {"id": 1}}, format="json").json()
        assert resp["owner"]["id"] == 1
