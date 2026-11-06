import pytest
from django.utils import timezone
from model_bakery.baker import make

from hawc.apps.vocab.constants import Ontology
from hawc.apps.vocab.models import Entity, Term
from hawc.apps.vocab.serializers import EntitySerializer, SimpleTermSerializer, TermSerializer


@pytest.mark.django_db
def test_term_serializer_bulk_create_and_deprecated():
    data = [
        {"uid": 8600, "name": "active", "type": 1},
        {"uid": 8601, "name": "old", "type": 1, "deprecated": True},
    ]
    serializer = TermSerializer(data=data, many=True)
    assert serializer.is_valid(), serializer.errors
    created = serializer.save()
    assert created[0].deprecated_on is None
    assert created[1].deprecated_on is not None


@pytest.mark.django_db
def test_term_serializer_bulk_update_partial():
    first = make(Term, uid=8610, name="before")
    second = make(Term, uid=8611, name="unchanged")
    serializer = TermSerializer(
        instance=Term.objects.filter(pk__in=[first.pk, second.pk]),
        data=[{"id": first.id, "name": "after"}, {"id": second.id, "name": second.name}],
        many=True,
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert [item.id for item in updated] == [first.id]
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.name == "after"
    assert second.name == "unchanged"


@pytest.mark.django_db
def test_simple_and_entity_serializers():
    term = make(Term, uid=8620, name="simple")
    assert SimpleTermSerializer(term).data == {"id": term.id, "name": "simple"}
    entity = make(Entity, ontology=Ontology.umls, uid="C8620")
    data = EntitySerializer(entity).data
    assert data["uid"] == "C8620"
    assert set(data) == {"id", "ontology", "uid"}


@pytest.mark.django_db
def test_serializer_validation_helpers():
    serializer = TermSerializer(many=True)
    instance = make(Term, uid=8910)
    assert serializer.values_equal(instance, "deprecated_on", timezone.now()) is False
    assert serializer.values_equal(instance, "name", instance.name) is True
    assert EntitySerializer().get_unique_together_validators() == []
