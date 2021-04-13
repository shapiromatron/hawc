from datetime import datetime

from rest_framework import serializers

from ..common.serializers import BulkSerializer
from . import models


class TermBulkSerializer(BulkSerializer):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "uid": {"type": "number"},
                "namespace": {"type": "number"},
                "parent_id": {"type": "number"},
                "type": {"type": "number"},
                "name": {"type": "string"},
                "notes": {"type": "string"},
                "deprecated": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    }

    def values_equal(self, instance, field, value):
        # equality for deprecated_on is whether it needs to be set
        if field == "deprecated_on":
            return bool(instance.deprecated_on) == bool(value)
        return super().values_equal(instance, field, value)


class TermSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False, write_only=True)
    deprecated = serializers.BooleanField(required=False, write_only=True)

    def validate(self, data):
        deprecated = data.pop("deprecated", None)
        if deprecated is not None:
            data["deprecated_on"] = datetime.now() if deprecated else None
        return data

    class Meta:
        model = models.Term
        fields = "__all__"
        list_serializer_class = TermBulkSerializer


class SimpleTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = ("id", "name")


class EntitySerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        return []

    class Meta:
        model = models.Entity
        fields = ("id", "ontology", "uid")
