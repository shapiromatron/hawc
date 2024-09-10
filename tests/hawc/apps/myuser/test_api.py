import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_api_auth_login(db_keys):
    """
    Users can successfully (and unsuccessfully) retrieve an API token
    """
    url = reverse("user:api_token_auth")
    factory = APIClient()

    # failure
    response = factory.post(url, {"username": db_keys.pm_user.email, "password": "wrong-password"})
    assert response.status_code == 400
    assert response.json() == {"non_field_errors": ["Unable to log in with provided credentials."]}

    # success
    response = factory.post(
        url, {"username": db_keys.pm_user.email, "password": db_keys.pm_user.password}
    )
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.django_db
def test_throttle(db_keys):
    """
    Test that throttling works as expected for short bursts
    """
    url = reverse("user:api_token_auth")
    factory = APIClient()

    throttled = False
    for _i in range(10):
        response = factory.post(
            url, {"username": db_keys.pm_user.email, "password": "wrong-password"}
        )
        assert response.status_code in [400, 429]
        if response.status_code == 429:
            assert response.json() == {"detail": "Request was throttled."}
            throttled = True
            break

    if not throttled:
        raise ImproperlyConfigured("Throttling was not enabled for burst authentication request")


@pytest.mark.django_db
def test_api_validate_token(db_keys):
    """
    Test that api returns a success message when user has an authtoken
    and returns a 403 code when the user does not
    """

    # failure
    url = reverse("user:api_token_validate")
    factory = APIClient()
    response = factory.get(url)
    assert response.status_code == 403
    assert response.json() == {"detail": "Authentication credentials were not provided."}

    # success
    assert factory.login(username="reviewer@hawcproject.org", password="pw") is True
    response = factory.get(url)
    assert response.status_code == 200
    assert response.json()["valid"] is True
