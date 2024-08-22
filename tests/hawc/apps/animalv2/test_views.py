import pytest
from django.test.client import Client
from django.urls import reverse


@pytest.mark.django_db
class TestViewPermissions:
    def test_success(self, db_keys):
        clients = [
            "admin@hawcproject.org",
            "pm@hawcproject.org",
            "team@hawcproject.org",
            "reviewer@hawcproject.org",
        ]
        views = [
            reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)),
        ]
        for client in clients:
            c = Client()
            assert c.login(username=client, password="pw") is True
            for view in views:
                response = c.get(view)
                assert response.status_code == 200

    def test_failure(self, db_keys):
        # anonymous user
        c = Client()
        views = [
            (reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)), 403),
        ]
        for url, status in views:
            response = c.get(url)
            assert response.status_code == status
