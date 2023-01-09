from rest_framework import serializers

from ..common.helper import SerializerHelper
from ..epi.serializers import ResultMetricSerializer
from ..study.serializers import StudySerializer
from . import models


class SingleResultSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    meta_result = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["estimateFormatted"] = instance.estimate_formatted
        return ret

    class Meta:
        model = models.SingleResult
        fields = "__all__"


class MetaResultLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.MetaResult
        fields = ("id", "label", "url")


class MetaProtocolSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    inclusion_criteria = serializers.StringRelatedField(many=True)
    exclusion_criteria = serializers.StringRelatedField(many=True)
    url = serializers.ReadOnlyField(source="get_absolute_url")
    protocol_type = serializers.ReadOnlyField(source="get_protocol_type_display")
    lit_search_strategy = serializers.ReadOnlyField(source="get_lit_search_strategy_display")
    results = MetaResultLinkSerializer(many=True)

    class Meta:
        model = models.MetaProtocol
        fields = "__all__"


class MetaResultSerializer(serializers.ModelSerializer):
    protocol = MetaProtocolSerializer()
    url = serializers.ReadOnlyField(source="get_absolute_url")
    metric = ResultMetricSerializer()
    adjustment_factors = serializers.StringRelatedField(many=True)
    single_results = SingleResultSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["estimateFormatted"] = instance.estimate_formatted
        return ret

    class Meta:
        model = models.MetaResult
        fields = "__all__"


SerializerHelper.add_serializer(models.MetaProtocol, MetaProtocolSerializer)
SerializerHelper.add_serializer(models.MetaResult, MetaResultSerializer)
