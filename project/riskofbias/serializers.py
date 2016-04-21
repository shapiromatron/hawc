from rest_framework import serializers

from . import models


class RiskOfBiasDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasDomain


class RiskOfBiasMetricSerializer(serializers.ModelSerializer):
    domain = RiskOfBiasDomainSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasMetric


class RiskOfBiasScoreSerializer(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super(RiskOfBiasScoreSerializer, self).to_representation(instance)
        ret['score_description'] = instance.get_score_display()
        ret['score_symbol'] = instance.score_symbol
        ret['score_shade'] = instance.score_shade
        ret['url_edit'] = instance.riskofbias.get_edit_url()
        ret['url_delete'] = instance.riskofbias.get_delete_url()
        return ret

    class Meta:
        model = models.RiskOfBiasScore
        fields = ('id', 'score', 'notes', 'metric')


class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(read_only=True, many=True)

    class Meta:
        model = models.RiskOfBias
        fields = ('id', 'author', 'conflict_resolution', 'study', 'created', 'last_updated', 'scores')
