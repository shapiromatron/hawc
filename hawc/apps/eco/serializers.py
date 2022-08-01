from rest_framework import serializers

from ..common.serializers import validate_jsonschema
from . import models


class NestedTermSerializer(serializers.Serializer):
    tree = serializers.JSONField()

    tree_schema = {
        "$id": "tree",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$defs": {
            "tagNode": {
                "type": "object",
                "additionalProperties": False,
                "required": ["data"],
                "properties": {
                    "id": {"type": "integer"},
                    "data": {
                        "type": "object",
                        "required": ["name"],
                        "additionalProperties": True,
                        "properties": {
                            "name": {"type": "string", "minLength": 1, "maxLength": 128},
                        },
                    },
                    "children": {"type": "array", "items": {"$ref": "#/$defs/tagNode"}},
                },
            }
        },
        "type": "array",
        "items": {"$ref": "#/$defs/tagNode"},
    }

    def validate_tree(self, value):
        return validate_jsonschema(value, self.tree_schema)

    def create(self, validated_data):
        loaded = models.NestedTerm.load_bulk(self.validated_data["tree"], None)
        return models.NestedTerm.objects.get(id=loaded[0])

    def to_representation(self, instance):
        tree = models.NestedTerm.dump_bulk(instance, keep_ids=True)
        return {"tree": tree}
