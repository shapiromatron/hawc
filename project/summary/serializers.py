import json

from rest_framework import serializers

from utils.helper import SerializerHelper

from . import models


class DataPivotSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(DataPivotSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['visual_type'] = instance.visual_type
        return ret

    class Meta:
        model = models.DataPivot


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

        ret['url_update'] = instance.get_update_url()
        ret['url_delete'] = instance.get_delete_url()

        eps = []
        qs = instance.get_endpoints()
        for e in qs:
            eps.append(SerializerHelper.get_serialized(e.endpoint, json=False))
        ret["endpoints"] = eps

        return ret
