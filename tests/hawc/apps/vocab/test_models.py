from datetime import datetime, timedelta
import pytest
from django.utils import timezone

from hawc.apps.vocab.models import Term, Entity, EntityTermRelation

# Simple bakery-style helper for creating test data
def bake(model, **kwargs):
    """Create and save a model instance."""
    obj = model(**kwargs)
    obj.save()
    return obj


@pytest.mark.django_db
class TestTerm:
    """Comprehensive tests for Term model."""

    def test_term_creation_basic(self):
        """Test creating a basic Term with minimal fields."""
        term = bake(
            Term,
            namespace=1,  # EHV
            type=1,  # system
            name="Test System Value",
            uid=1000
        )

        assert str(term) == "EHV::system::Test System Value"
        assert term.namespace == 1
        assert term.type == 1
        assert term.name == "Test System Value"
        assert term.uid is not None
        assert term.parent is None
        assert term.notes == ""
        assert term.deprecated_on is None

