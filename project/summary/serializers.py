import json

from rest_framework import serializers

from utils.helper import SerializerHelper

from . import models


class CollectionVisualSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(CollectionVisualSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['visual_type'] = instance.get_visual_type_display()
        ret["settings"] = json.loads(instance.settings)
        return ret

    class Meta:
        model = models.Visual
        exclude = ('endpoints', )


class VisualSerializer(CollectionVisualSerializer):

    def to_representation(self, instance):
        ret = super(VisualSerializer, self).to_representation(instance)
        eps = []
        qs = instance.get_endpoints()
        for e in qs:
            eps.append(SerializerHelper.get_serialized(e.endpoint, json=False))
        ret["endpoints"] = eps

        return ret
