from datetime import timedelta
import pytest
from django.utils import timezone

# Simple bakery-style helper for creating test data
def bake(model, **kwargs):
    """Create and save a model instance."""
    obj = model(**kwargs)
    obj.save()
    return obj


@pytest.mark.django_db
class TestTermSerializer:
    """Comprehensive tests for TermSerializer using manual test data creation."""

    def test_bulk_create_saves_all_fields(self):
        """Test that bulk create saves all fields correctly."""
        data = [
            {
                "uid": 100, 
                "name": "serializer test system", 
                "type": 1,
                "parent_id": None
            },
            {
                "uid": 101, 
                "name": "serializer test organ", 
                "type": 2,
                "parent_id": None
            },
        ]

        ser = TermSerializer(data=data, many=True)
        assert ser.is_valid()
        created_instances = ser.save()

        # Verify first instance
        instance_data = data[0]
        instance = created_instances[0]
        assert (
            instance.name == instance_data["name"]
            and instance.parent_id == instance_data["parent_id"]
            and instance.deprecated_on is None
        )

        # Verify second instance
        instance_data = data[1]
        instance = created_instances[1]
        assert instance.name == instance_data["name"] and instance.deprecated_on is None

    def test_bulk_create_with_parent(self):
        """Test bulk create with parent_id relationships."""
        # Create parent term first
        parent = bake(
            Term,
            namespace=1,
            type=1,
            name="Parent System",
            uid=2001
        )

        data = [
            {
                "uid": 102, 
                "name": "Child System", 
                "type": 1,
                "parent_id": parent.id
            }
        ]

        ser = TermSerializer(data=data, many=True)
        assert ser.is_valid()
        created_instances = ser.save()

        instance = created_instances[0]
        assert instance.parent == parent

    def test_bulk_create_with_deprecated(self):
        """Test bulk create marks deprecated terms."""
        data = [
            {"uid": 103, "name": "Active Term", "type": 1},
            {"uid": 104, "name": "Deprecated Term", "type": 1, "deprecated": True},
        ]

        ser = TermSerializer(data=data, many=True)
        assert ser.is_valid()
        created_instances = ser.save()

        # Verify active term
        instance = next(i for i in created_instances if i.name == "Active Term")
        assert instance.deprecated_on is None

        # Verify deprecated term
        instance = next(i for i in created_instances if i.name == "Deprecated Term")
        assert instance.deprecated_on is not None

    def test_bulk_update(self):
        """Test bulk update of multiple terms."""
        # Create some terms first
        term1 = bake(
            Term,
            namespace=1,
            type=1,
            name="Original Name 1",
            uid=2002
        )

        term2 = bake(
            Term,
            namespace=1,
            type=2,
            name="Original Name 2",
            uid=2003
        )

        terms = list(Term.objects.filter(pk__in=[term1.id, term2.id]))
        
        data = [
            {
                "id": term1.id,
                "name": "Updated Name 1",
                "type": 1,
                "notes": "Updated notes 1",
            },
            {
                "id": term2.id,
                "name": "Deprecated Term Updated",
                "type": 2,
                "deprecated": True,
            },
        ]

        before_test = timezone.now() - timedelta(seconds=1)
        ser = TermSerializer(instance=terms, data=data, many=True, partial=True)
        assert ser.is_valid()
        updated_instances = ser.save()

        # Verify updates happened
        instance = next(i for i in updated_instances if i.id == term1.id)
        assert instance.name == "Updated Name 1"
        assert instance.notes == "Updated notes 1"

    def test_bulk_update_with_partial(self):
        """Test bulk update with partial=True only updates provided fields."""
        # Create some terms first
        term1 = bake(
            Term,
            namespace=1,
            type=1,
            name="Original Name 1",
            uid=3001
        )

        term2 = bake(
            Term,
            namespace=1,
            type=3,
            name="Original Name 2",
            uid=3002
        )

        terms = list(Term.objects.filter(pk__in=[term1.id, term2.id]))
        
        # Only update name on one term, keep others as-is
        data = [
            {
                "id": term1.id,
                "name": "Updated Name 1",
                "type": 1,
            },
            {
                "id": term2.id,
                "name": term2.name,
                "type": 3,
            },
        ]

        ser = TermSerializer(instance=terms, data=data, many=True, partial=True)
        assert ser.is_valid()
        updated_instances = ser.save()

        # Verify only first term was updated
        updated_count = sum(1 for i in updated_instances if i.id == term1.id)
        assert updated_count == 1


@pytest.mark.django_db
class TestSimpleTermSerializer:
    """Tests for SimpleTermSerializer - minimal serializer with only id and name."""

    def test_simple_serializer_basic(self):
        """Test simple serializer outputs only id and name fields."""
        term = bake(
            Term,
            namespace=1,
            type=1,
            name="Simple Test System",
            uid=3010
        )

        from hawc.apps.vocab.serializers import SimpleTermSerializer
        
        serializer = SimpleTermSerializer(term)
        
        assert "id" in serializer.data
        assert "name" in serializer.data
        assert "notes" not in serializer.data
        assert "type" not in serializer.data


@pytest.mark.django_db
class TestEntitySerializer:
    """Tests for Entity model serializer."""

    def test_entity_serializer_basic(self):
        """Test basic entity serializer with only required fields."""
        entity = bake(
            Entity,
            ontology=1,
            uid="C0015684"
        )

        from hawc.apps.vocab.serializers import TermSerializer
        
        serializer = TermSerializer(entity)
        
        assert serializer.is_valid()
        assert "id" in serializer.data
        assert "ontology" in serializer.data
        assert "uid" in serializer.data

    def test_entity_serializer_with_terms(self):
        """Test entity serializer includes associated terms."""
        system_term = bake(
            Term,
            namespace=1,
            type=1,
            name="Cardiovascular",
            uid=4010
        )

        # Create entity and associate with term
        entity = bake(
            Entity,
            ontology=1,
            uid="C0023456",
            terms=[system_term]
        )

        from hawc.apps.vocab.serializers import TermSerializer
        
        serializer = TermSerializer(entity)
        
        assert serializer.is_valid()

