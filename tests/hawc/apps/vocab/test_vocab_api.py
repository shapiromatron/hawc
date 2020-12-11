import pytest
from django.test.client import Client
from django.urls import reverse


@pytest.mark.django_db
class TestEhvTermViewset:
    def test_permissions(self):
        url = reverse("vocab:api:ehv-system")
        anon_client = Client()
        auth_client = Client()
        assert auth_client.login(username="team@hawcproject.org", password="pw") is True
        assert anon_client.get(url).status_code == 403
        assert auth_client.get(url).status_code == 200

    def test_expected_response(self):
        client = Client()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        test_cases = [
            # test urls resolve
            (reverse("vocab:api:ehv-system"), [{"id": 1, "name": "Cardiovascular"}]),
            (reverse("vocab:api:ehv-organ"), [{"id": 2, "name": "Serum"}]),
            (reverse("vocab:api:ehv-effect"), [{"id": 3, "name": "Fatty Acids"}]),
            (reverse("vocab:api:ehv-effect-subtype"), [{"id": 4, "name": "Clinical Chemistry"}]),
            (reverse("vocab:api:ehv-endpoint-name"), [{"id": 5, "name": "Fatty Acid Balance"}]),
        ]

        for url, resp in test_cases:
            assert client.get(url).json() == resp

    def test_query_params(self):
        client = Client()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        test_cases = [
            # test term lookup
            (
                reverse("vocab:api:ehv-endpoint-name") + "?term=Acid",
                [{"id": 5, "name": "Fatty Acid Balance"}],
            ),
            (reverse("vocab:api:ehv-endpoint-name") + "?term=NONE", []),
            # test parent lookup
            (
                reverse("vocab:api:ehv-endpoint-name") + "?parent=4",
                [{"id": 5, "name": "Fatty Acid Balance"}],
            ),
            (reverse("vocab:api:ehv-endpoint-name") + "?parent=3", []),
            (
                reverse("vocab:api:ehv-endpoint-name") + "?parent=text",
                [{"id": 5, "name": "Fatty Acid Balance"}],
            ),
        ]

        for url, resp in test_cases:
            assert client.get(url).json() == resp
