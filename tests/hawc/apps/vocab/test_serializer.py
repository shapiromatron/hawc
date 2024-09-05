from datetime import timedelta

import pytest
from django.utils import timezone

from hawc.apps.vocab.models import Term
from hawc.apps.vocab.serializers import TermSerializer


@pytest.mark.django_db
class TestTermSerializer:
    def test_bulk_create(self):
        data = [
            {"uid": 100, "name": "serializer test 1", "type": 1, "parent_id": 1},
            {"uid": 101, "name": "serializer test 2", "type": 1, "deprecated": True},
        ]
        ser = TermSerializer(data=data, many=True)
        assert ser.is_valid()
        created_instances = ser.save()

        instance_data = data[0]
        instance = created_instances[0]
        assert (
            instance.name == instance_data["name"]
            and instance.parent.id == instance_data["parent_id"]
            and instance.deprecated_on is None
        )

        instance_data = data[1]
        instance = created_instances[1]
        assert instance.name == instance_data["name"] and instance.deprecated_on is not None

    def test_bulk_update(self):
        unchanged_term = Term.objects.get(pk=3)
        terms = Term.objects.filter(pk__in=[1, 2, 3])
        data = [
            {
                "id": 1,
                "name": "serializer test name",
                "type": 1,
                "notes": "serializer test notes",
                "parent_id": 1,
            },
            {"id": 2, "name": "Serum", "type": 1, "deprecated": True},
            {"id": unchanged_term.id, "name": unchanged_term.name},
        ]
        before_test = timezone.now() - timedelta(seconds=1)
        ser = TermSerializer(instance=terms, data=data, many=True, partial=True)
        assert ser.is_valid()
        updated_instances = ser.save()

        with pytest.raises(StopIteration):
            next(instance for instance in updated_instances if instance.id == unchanged_term.id)

        instance_data = data[0]
        instance = next(
            instance for instance in updated_instances if instance.id == instance_data["id"]
        )
        assert (
            instance.name == instance_data["name"]
            and instance.notes == instance_data["notes"]
            and instance.parent.id == instance_data["parent_id"]
        )

        instance_data = data[1]
        instance = next(
            instance for instance in updated_instances if instance.id == instance_data["id"]
        )
        assert instance.deprecated_on > before_test and instance.last_updated > before_test
