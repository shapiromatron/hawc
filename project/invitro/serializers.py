import json

from rest_framework import serializers

from study.serializers import StudySerializer
from utils.helper import SerializerHelper

from . import models


class IVCellTypeSerializer(serializers.ModelSerializer):
    sex_symbol = serializers.CharField(source='get_sex_symbol', read_only=True)

    def transform_sex(self, obj, value):
        return obj.get_sex_display()

    class Meta:
        model = models.IVCellType


class IVExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    cell_type = IVCellTypeSerializer()
    metabolic_activation_symbol = serializers.CharField(source='get_metabolic_activation_display', read_only=True)

    class Meta:
        model = models.IVExperiment
        depth = 1


class IVChemicalSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IVChemical


class IVEndpointGroupSerializer(serializers.ModelSerializer):

    def transform_difference_control(self, obj, value):
        return obj.get_difference_control_display()

    def transform_significant_control(self, obj, value):
        return obj.get_significant_control_display()

    def transform_cytotoxicity_observed(self, obj, value):
        return obj.get_cytotoxicity_observed_display()

    class Meta:
        model = models.IVEndpointGroup


class IVBenchmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IVBenchmark


class IVEndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField()
    chemical = IVChemicalSerializer()
    experiment = IVExperimentSerializer()
    groups = IVEndpointGroupSerializer(many=True)
    benchmarks = IVBenchmarkSerializer(many=True)

    def transform_data_type(self, obj, value):
        return obj.get_data_type_display()

    def transform_variance_type(self, obj, value):
        return obj.get_variance_type_display()

    def transform_observation_time_units(self, obj, value):
        return obj.get_observation_time_units_display()

    def transform_monotonicity(self, obj, value):
        return obj.get_monotonicity_display()

    def transform_overall_pattern(self, obj, value):
        return obj.get_overall_pattern_display()

    def transform_trend_test(self, obj, value):
        return obj.get_trend_test_display()

    def transform_additional_fields(self, obj, value):
        return json.loads(obj.additional_fields)

    class Meta:
        model = models.IVEndpoint
        depth = 1


SerializerHelper.add_serializer(models.IVEndpoint, IVEndpointSerializer)
