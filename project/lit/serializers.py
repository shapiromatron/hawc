from rest_framework import serializers
from rest_framework.exceptions import ParseError

from . import models


class IdentifiersSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(IdentifiersSerializer, self).to_representation(instance)
        ret['database'] = instance.get_database_display()
        ret['url'] = instance.get_url()
        return ret

    class Meta:
        model = models.Identifiers


class ReferenceTagsSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        raise ParseError("Not implemented!")

    def to_representation(self, obj):
        # obj is a model-manager in this case; convert to list to serialize
        return list(obj.values('id', 'name'))
