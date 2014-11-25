from rest_framework import serializers

from study.serializers import StudySerializer

from utils.helper import SerializerHelper

from . import models


class AssessedOutcomeSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = models.AssessedOutcome
        depth = 0


class AssessedOutcomeGroupSerializer(serializers.ModelSerializer):
    assessed_outcome = AssessedOutcomeSerializer()

    class Meta:
        model = models.AssessedOutcomeGroup
        depth = 0


class SingleResultSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    outcome_group = AssessedOutcomeGroupSerializer()
    meta_result = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = models.SingleResult
        depth = 1


class MetaProtocolSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    study = StudySerializer()

    def transform_protocol_type(self, obj, value):
        return obj.get_protocol_type_display()

    def transform_lit_search_strategy(self, obj, value):
        return obj.get_lit_search_strategy_display()

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


SerializerHelper.add_serializer(models.AssessedOutcome, AssessedOutcomeSerializer)
SerializerHelper.add_serializer(models.AssessedOutcomeGroup, AssessedOutcomeGroupSerializer)
SerializerHelper.add_serializer(models.SingleResult, SingleResultSerializer)
SerializerHelper.add_serializer(models.MetaProtocol, MetaProtocolSerializer)
SerializerHelper.add_serializer(models.Factor, FactorSerializer)
SerializerHelper.add_serializer(models.MetaResult, MetaResultSerializer)
