from jsonschema import validate, ValidationError
from rest_framework import serializers

from . import models


class BMDModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BMDModel
        fields = (
            'id', 'model_id', 'bmr_id',
            'name', 'overrides', 'date_executed',
            'execution_error', 'outputs',
            'created', 'last_updated',
        )


class BMDSessionSerializer(serializers.ModelSerializer):
    allModelOptions = serializers.JSONField(source='get_model_options', read_only=True)
    allBmrOptions = serializers.JSONField(source='get_bmr_options', read_only=True)
    models = BMDModelSerializer(many=True)

    class Meta:
        model = models.BMDSession
        fields = (
            'id', 'bmrs', 'models',
            'allModelOptions', 'allBmrOptions',
        )


class BMDSessionUpdateSerializer(serializers.Serializer):
    bmrs = serializers.JSONField()
    modelSettings = serializers.JSONField()

    bmr_schema = schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'type': {'type': 'string'},
                'value': {'type': 'number'},
                'confidence_level': {'type': 'number'},
            },
            'required': ['type', 'value', 'confidence_level']
        },
        'minItems': 1,
    }

    model_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'overrides': {'type': 'object'},
                'defaults': {'type': 'object'},
            },
            'required': ['name', 'overrides', 'defaults']
        },
        'minItems': 1,
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
        self.instance.bmrs = self.validated_data['bmrs']
        self.instance.date_executed = None
        self.instance.save()

        self.instance.models.all().delete()
        objects = []
        for i, bmr in enumerate(self.validated_data['bmrs']):
            for j, settings in enumerate(self.validated_data['modelSettings']):
                obj = models.BMDModel(
                    session=self.instance,
                    bmr_id=i,
                    model_id=j,
                    name=settings['name'],
                    overrides=settings['overrides']
                )
                objects.append(obj)
        models.BMDModel.objects.bulk_create(objects)
