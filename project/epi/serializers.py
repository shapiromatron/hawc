from rest_framework import serializers

from study.serializers import StudySerializer

from . import models


class SingleResultSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    meta_result = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = models.SingleResult
        depth = 1


class MetaProtocolSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    protocol_type = serializers.CharField(source='get_protocol_type_display', read_only=True)
    lit_search_strategy = serializers.CharField(source='get_lit_search_strategy_display', read_only=True)
    study = StudySerializer()

    class Meta:
        model = models.MetaProtocol
        depth = 1


class FactorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Factor
        depth = 0


class MetaResultSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    protocol = MetaProtocolSerializer()
    adjustment_factors = FactorSerializer()
    single_results = SingleResultSerializer(many=True)

    class Meta:
        model = models.MetaResult
        depth = 4


