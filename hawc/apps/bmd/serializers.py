from copy import deepcopy

from jsonschema import ValidationError, validate
from rest_framework import serializers

from . import models


class LogicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LogicField
        fields = (
            "id",
            "name",
            "description",
            "failure_bin",
            "threshold",
            "continuous_on",
            "dichotomous_on",
            "cancer_dichotomous_on",
        )


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
    allModelOptions = serializers.JSONField(source="get_model_options", read_only=True)
    allBmrOptions = serializers.JSONField(source="get_bmr_options", read_only=True)
    selected_model = SelectedModelSerializer(source="get_selected_model", read_only=True)
    models = ModelSerializer(many=True)
    logic = LogicFieldSerializer(source="get_logic", many=True)

    class Meta:
        model = models.Session
        fields = (
            "id",
            "bmrs",
            "models",
            "dose_units",
            "allModelOptions",
            "allBmrOptions",
            "selected_model",
            "logic",
            "is_finished",
        )


class SessionUpdateSerializer(serializers.Serializer):
    bmrs = serializers.JSONField()
    modelSettings = serializers.JSONField()
    dose_units = serializers.IntegerField()

    bmr_schema = schema = {
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

    def validate_bmrs(self, value):
        try:
            validate(value, self.bmr_schema)
        except ValidationError as err:
            raise serializers.ValidationError(err.message)
        return value

    def validate_modelSettings(self, value):
        try:
            validate(value, self.model_schema)
        except ValidationError as err:
            raise serializers.ValidationError(err.message)
        return value

    def save(self):
        self.instance.bmrs = self.validated_data["bmrs"]
        self.instance.date_executed = None
        self.instance.dose_units_id = self.validated_data["dose_units"]
        self.instance.save()

        self.instance.models.all().delete()
        objects = []
        for i, bmr in enumerate(self.validated_data["bmrs"]):
            bmr_overrides = self.instance.get_bmr_overrides(self.instance.get_session(), i)
            for j, settings in enumerate(self.validated_data["modelSettings"]):
                overrides = deepcopy(settings["overrides"])
                overrides.update(bmr_overrides)
                obj = models.Model(
                    session=self.instance,
                    bmr_id=i,
                    model_id=j,
                    name=settings["name"],
                    overrides=overrides,
                )
                objects.append(obj)
        models.Model.objects.bulk_create(objects)


class SelectedModelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SelectedModel
        fields = ("id", "model", "notes")

    def save(self):
        session = self.context["session"]
        data = self.validated_data
        obj, _ = models.SelectedModel.objects.update_or_create(
            endpoint_id=session.endpoint_id,
            dose_units_id=session.dose_units_id,
            defaults={"model": data["model"], "notes": data["notes"]},
        )
        self.instance = obj
        return self.instance
