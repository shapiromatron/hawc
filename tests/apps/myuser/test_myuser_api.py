import pytest
from rest_framework.test import APIClient
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured


@pytest.mark.django_db
def test_api_auth_login(authenticated_user):
    """
    Users can successfully (and unsuccessfully) retrieve an API token
    """
    url = reverse("user:api_token_auth")
    factory = APIClient()

    # failure
    response = factory.post(url, {"username": "me@me.com", "password": "nope"})
    assert response.status_code == 400
    assert response.json() == {"non_field_errors": ["Unable to log in with provided credentials."]}

    # success
    response = factory.post(url, {"username": "me@me.com", "password": "pw"})
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.django_db
def test_throttle():
    """
    Test that throttling works as expected for short bursts
    """
    url = reverse("user:api_token_auth")
    factory = APIClient()

    throttled = False
    for i in range(10):
        response = factory.post(url, {"username": "me@me.com", "password": "nope"})
        assert response.status_code in [400, 429]
        if response.status_code == 429:
            assert response.json() == {"detail": "Request was throttled."}
            throttled = True
            break

    if not throttled:
        raise ImproperlyConfigured("Throttling was not enabled for burst authentication request")
