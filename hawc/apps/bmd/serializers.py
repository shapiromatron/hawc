from rest_framework import serializers

from ..common.serializers import validate_jsonschema
from . import constants, models


class SelectedModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SelectedModel
        fields = ("id", "dose_units", "model", "notes")


class ModelSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    dose_units = serializers.IntegerField(source="session.dose_units_id", read_only=True)

    class Meta:
        model = models.Model
        fields = (
            "id",
            "url",
            "dose_units",
            "model_id",
            "bmr_id",
            "name",
            "overrides",
            "date_executed",
            "execution_error",
            "output",
            "outfile",
            "created",
            "last_updated",
        )


class SessionSerializer(serializers.ModelSerializer):
    model_options = serializers.JSONField(source="get_model_options", read_only=True)
    bmr_options = serializers.JSONField(source="get_bmr_options", read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["logic"] = constants.bmds2_logic()
        return ret

    class Meta:
        model = models.Session
        fields = (
            "id",
            "inputs",
            "outputs",
            "dose_units",
            "model_options",
            "bmr_options",
            "selected",
            "is_finished",
        )


class SessionUpdateSerializer(serializers.Serializer):
    inputs = serializers.JSONField()
    modelSettings = serializers.JSONField()
    dose_units = serializers.IntegerField()

    input_schema = {
        "type": "object",
        "properties": {
            "bmrs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "value": {"type": "number"},
                        "confidence_level": {"type": "number"},
                    },
                    "required": ["type", "value", "confidence_level"],
                },
                "minItems": 1,
            }
        },
        "required": ["bmrs"],
    }

    model_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "overrides": {"type": "object"},
                "defaults": {"type": "object"},
            },
            "required": ["name", "overrides", "defaults"],
        },
        "minItems": 1,
    }

    def validate_inputs(self, value):
        return validate_jsonschema(value, self.input_schema)

    def validate_modelSettings(self, value):
        return validate_jsonschema(value, self.model_schema)

    def save(self):
        raise NotImplementedError()


class SelectedModelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SelectedModel
        fields = ("id", "model", "notes")

    def save(self):
        raise NotImplementedError()
