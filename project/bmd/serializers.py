import json

from rest_framework import serializers

from . import models


class BMDSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BMD_session


class BMDModelRunSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(BMDModelRunSerializer, self).to_representation(instance)

        ret['dose_units_id'] = instance.BMD_session.dose_units.id
        ret['option_defaults'] = json.loads(instance.option_defaults),
        ret['option_override'] = json.loads(instance.option_override),
        ret['option_override_text'] = json.loads(instance.option_override_text),

        ret['plotting'] = 'error'
        ret['outputs'] = 'error'
        if not instance.runtime_error:
            ret['plotting'] = json.loads(instance.d3_plotting)
            ret['outputs'] = json.loads(instance.outputs)

        if instance.plot and instance.plot.url:
            ret['bmds_plot_url'] = instance.plot.url

        return ret

    class Meta:
        model = models.BMD_model_run
