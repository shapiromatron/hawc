import pytest
from rest_framework.test import APIClient, force_authenticate
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.vocab.models import Term

@pytest.fixture(scope='function')
def test_user():
    email = "test_api_user@hawcproject.org"
    user = HAWCUser.objects.create_user(email=email, password="testpass123")
    yield user
    # Cleanup  
    user.delete()

@pytest.mark.django_db
class TestEhvTermViewSet:
    def test_system_action_authenticated(self, test_user):
        """Test GET /vocab/api/ehv/?system=True (the system action) returns 200."""
        
        # Create some terms first
        term1 = Term.objects.create(namespace=1, type=1, name="Cardiovascular", uid=5000)
        term2 = Term.objects.create(namespace=1, type=1, name="Immunotoxicity", uid=5010)
        
        client = APIClient()
        
        url = '/vocab/api/ehv/?system=True'
        
        # Use the standard DRF pattern - force_authenticate modifies request in place
        # The key is that we need to make the authenticated request before calling get()
        with client:
            client.force_authenticate(user=test_user)
            response = client.get(url)
            
            assert response.status_code == 200

