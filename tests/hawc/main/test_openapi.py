import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.myuser.models import HAWCUser


@pytest.mark.django_db
def test_openapi():
    # staff user and non staff user
    staff = HAWCUser.objects.get(email="admin@hawcproject.org")
    user = HAWCUser.objects.get(email="team@hawcproject.org")
    assert staff.is_staff and not user.is_staff

    # login using these users
    staff_client = APIClient()
    user_client = APIClient()
    assert staff_client.login(username=staff.email, password="pw")
    assert user_client.login(username=user.email, password="pw")

    # staff can access OpenAPI, non staff cannot
    url = reverse("openapi")
    assert staff_client.get(url).status_code == 200
    assert user_client.get(url).status_code == 403
