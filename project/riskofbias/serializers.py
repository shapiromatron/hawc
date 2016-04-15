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

class RiskOfBiasScoreSerializer(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasScore
        fields = ('id', 'score', 'notes', 'metric')

class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(read_only=True, many=True)

    class Meta:
        model = models.RiskOfBias
        fields = ('id', 'author', 'conflict_resolution', 'study', 'created', 'last_updated', 'scores')
