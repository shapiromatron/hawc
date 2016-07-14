from jsonschema import validate, ValidationError
from rest_framework import serializers

from . import models, tasks


class BMDSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BMDSession
        fields = ('id', )

    def to_representation(self, instance):
        ret = super(BMDSessionSerializer, self).to_representation(instance)
        ret['models'] = []
        ret['bmrs'] = []
        ret['allModelOptions'] = instance.get_model_options()
        ret['allBmrOptions'] = instance.get_bmr_options()
        return ret


class BMDSessionUpdateSerializer(serializers.Serializer):
    bmrs = serializers.JSONField()
    models = serializers.JSONField()

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

    def validate_models(self, value):
        try:
            validate(value, self.model_schema)
        except ValidationError as err:
            raise serializers.ValidationError(err.message)
        return value

    def save(self):
        self.instance.date_executed = None
        self.instance.save()
        tasks.execute.delay(self.instance.id)
