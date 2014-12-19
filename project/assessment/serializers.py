from rest_framework import serializers
from rest_framework.exceptions import ParseError


class EffectTagsSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        raise ParseError("Not implemented!")

    def to_representation(self, obj):
        # obj is a model-manager in this case; convert to list to serialize
        return list(obj.values('slug', 'name'))
