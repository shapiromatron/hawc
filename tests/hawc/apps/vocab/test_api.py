import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType
from hawc.apps.myuser.models import HAWCUser
from . import Term

def bake(model, **kwargs):
    obj = model(**kwargs)
    obj.save()
    return obj

@pytest.fixture(scope='function')
def auth_client():
    username = "team@hawcproject.org"
    password = "testpassword123"
    user = HAWCUser.objects.get_or_create(email=username, defaults={'username': username.split('@')[0]})[0]
    user.set_password(password)
    user.save()
    
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
class TestEhvTermViewSet:
    def test_permissions_anonymous_blocked(self):
        client = APIClient()
        url = reverse("vocab:api:ehv-system")
        response = client.get(url)
        assert response.status_code == 403

    def test_permissions_authenticated_success(self, auth_client):
        term1 = bake(Term, namespace=1, type=1, name="Cardiovascular", uid=5000)
        term2 = bake(Term, namespace=1, type=1, name="Immunotoxicity", uid=5010)
        url = reverse("vocab:api:ehv-system")
        response = auth_client.get(url)
        assert response.status_code == 200
