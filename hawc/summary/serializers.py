import json

from rest_framework import serializers

from utils.helper import SerializerHelper

from . import models


class CollectionDataPivotSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['visual_type'] = instance.visual_type
        return ret

    class Meta:
        model = models.DataPivot
        exclude = ('settings', )


class DataPivotSerializer(CollectionDataPivotSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["settings"] = instance.get_settings()
        ret['data_url'] = instance.get_data_url()
        ret['download_url'] = instance.get_download_url()
        return ret


class CollectionVisualSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['visual_type'] = instance.get_rob_visual_type_display(instance.get_visual_type_display())
        try:
            settings = json.loads(instance.settings)
        except json.JSONDecodeError:
            settings = {}
        ret["settings"] = settings
        return ret

    class Meta:
        model = models.Visual
        exclude = ('endpoints', 'studies', )


class VisualSerializer(CollectionVisualSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['url_update'] = instance.get_update_url()
        ret['url_delete'] = instance.get_delete_url()

        ret["endpoints"] = [
            SerializerHelper.get_serialized(d, json=False)
            for d in instance.get_endpoints()
        ]

        ret["studies"] = [
            SerializerHelper.get_serialized(d, json=False)
            for d in instance.get_studies()
        ]

        ret["assessment_rob_name"] = instance.assessment.get_rob_name_display()

        return ret


SerializerHelper.add_serializer(models.Visual, VisualSerializer)
