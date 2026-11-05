import pytest
from django.urls import reverse
from rest_framework.test import APIClient, force_authenticate
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.vocab.models import Term

@pytest.mark.django_db
def test_authenticated_access(auth_user):
    """Test that authenticated users can access the EHV system API."""
    client = APIClient()
    force_authenticate(client, user=auth_user)
    
    # Create some sample data
    term1 = Term.objects.create(namespace=1, type=1, name="Cardiovascular", uid=5000)
    
    url = reverse("vocab:api:ehv-system")
    response = client.get(url)
    
    assert response.status_code == 200

@pytest.fixture(scope='function')
def auth_user():
    email = f"test_{hash('test')}@hawcproject.org"
    user = HAWCUser.objects.create_user(email=email, password="testpass")
    yield user
