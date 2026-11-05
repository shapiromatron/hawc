import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Simple bakery-style helper for creating test data
def bake(model, **kwargs):
    """Create and save a model instance."""
    obj = model(**kwargs)
    obj.save()
    return obj


@pytest.mark.django_db
class TestEhvBrowseView:
    """Tests for EHV browse view template rendering."""

    def test_ehv_browse_returns_200(self):
        """Test that EHV browse view returns 200 status code."""
        client = APIClient()
        
        # Create authenticated user
        username = "team@hawcproject.org"
        password = "testpassword123"
        auth_client = client
        auth_client.login(username=username, password=password)

        url = reverse("vocab:ehv-browse")
        response = auth_client.get(url)
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestToxRefDBBrowseView:
    """Tests for ToxRefDB browse view template rendering."""

    def test_toxrefdb_browse_returns_200(self):
        """Test that ToxRefDB browse view returns 200 status code."""
        client = APIClient()
        
        username = "team@hawcproject.org"
        password = "testpassword123"
        auth_client = client
        auth_client.login(username=username, password=password)

        url = reverse("vocab:toxrefdb-browse")
        response = auth_client.get(url)
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestViewIntegrationWithModelBaker:
    """Integration tests for views using manual test data creation."""

    def test_ehv_view_with_sample_data(self):
        """Test EHV browse view with sample vocabulary data created by bake()."""
        client = APIClient()
        
        # Create authenticated user
        username = "team@hawcproject.org"
        password = "testpassword123"
        auth_client = client
        auth_client.login(username=username, password=password)

        # Create sample terms for testing the browse view
        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Cardiovascular",
            uid=7001
        )

        organ_term = bake(
            Term,
            namespace=1,
            type=2,
            name="Serum",
            parent_id=system_term.id,
            uid=7002
        )

        effect_term = bake(
            Term,
            namespace=1,
            type=3,
            name="Fatty Acids",
            parent_id=organ_term.id,
            uid=7003
        )

        endpoint_name_term = bake(
            Term,
            namespace=1,
            type=5,
            name="Lipid Profile",
            parent_id=effect_term.id,
            uid=7004
        )

        url = reverse("vocab:ehv-browse")
        response = auth_client.get(url)
        
        assert response.status_code == 200

    def test_toxrefdb_view_with_sample_data(self):
        """Test ToxRefDB browse view with sample vocabulary data."""
        client = APIClient()
        
        username = "team@hawcproject.org"
        password = "testpassword123"
        auth_client = client
        auth_client.login(username=username, password=password)

        # Create sample terms for ToxRefDB testing
        system_term = bake(
            Term,
            namespace=2,
            type=1,
            name="systemic",
            uid=8001
        )

        effect_term = bake(
            Term,
            namespace=2,
            type=3,
            name="pathology_microscopic",
            parent_id=system_term.id,
            uid=8002
        )

        endpoint_name_term = bake(
            Term,
            namespace=2,
            type=5,
            name="dysplasia",
            parent_id=effect_term.id,
            uid=8003
        )

        url = reverse("vocab:toxrefdb-browse")
        response = auth_client.get(url)
        
        assert response.status_code == 200

