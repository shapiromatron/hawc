from rest_framework import serializers

from utils.helper import SerializerHelper

from myuser.serializers import HAWCUserSerializer
from . import models


class AssessmentMetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasMetric


class AssessmentDomainSerializer(serializers.ModelSerializer):
    metrics = AssessmentMetricSerializer(many=True)

    class Meta:
        model = models.RiskOfBiasDomain


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
    scores = RiskOfBiasScoreSerializer(read_only=False, many=True, partial=True)
    author = HAWCUserSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBias
        fields = ('id', 'author', 'active', 'final', 'study', 'created', 'last_updated', 'scores')

    def partial_update_scores(self, instance, score_data):
        scores = instance.scores.all()
        for form_data, score in zip(score_data, scores):
            for field, value in form_data.items():
                setattr(score, field, value)
            score.save()

    def update(self, instance, validated_data):
        score_data = validated_data.pop('scores')
        if score_data:
            self.partial_update_scores(instance, score_data)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return super(RiskOfBiasSerializer, self).update(instance, validated_data)

SerializerHelper.add_serializer(models.RiskOfBias, RiskOfBiasSerializer)
