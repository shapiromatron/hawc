from rest_framework import serializers

from lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from utils.helper import SerializerHelper

from . import models


class RiskOfBiasDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasDomain


class RiskOfBiasMetricSerializer(serializers.ModelSerializer):
    domain = RiskOfBiasDomainSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasMetric


class RiskOfBiasSerializer(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super(RiskOfBiasSerializer, self).to_representation(instance)
        ret['score_description'] = instance.get_score_display()
        ret['score_symbol'] = instance.score_symbol
        ret['score_shade'] = instance.score_shade
        ret['url_edit'] = instance.get_edit_url()
        ret['url_delete'] = instance.get_delete_url()
        return ret

    class Meta:
        model = models.RiskOfBias
        exclude = ('object_id', 'content_type')
