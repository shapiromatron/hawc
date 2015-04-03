import json
from collections import OrderedDict

from rest_framework import serializers

from study.serializers import StudySerializer
from utils.helper import SerializerHelper

from . import models


class IVCellTypeSerializer(serializers.ModelSerializer):
    sex_symbol = serializers.CharField(source='get_sex_symbol', read_only=True)

    def to_representation(self, instance):
        ret = super(IVCellTypeSerializer, self).to_representation(instance)
        ret['sex'] = instance.get_sex_display()
        return ret

    class Meta:
        model = models.IVCellType


class IVExperimentSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    cell_type = IVCellTypeSerializer()

    def to_representation(self, instance):
        ret = super(IVExperimentSerializer, self).to_representation(instance)
        ret['metabolic_activation_symbol'] = instance.get_metabolic_activation_display()
        return ret

    class Meta:
        model = models.IVExperiment
        depth = 1


class _IVChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IVChemical


class IVChemicalSerializer(_IVChemicalSerializer):
    study = StudySerializer()


class IVEndpointGroupSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(IVEndpointGroupSerializer, self).to_representation(instance)
        ret['difference_control'] = instance.get_difference_control_display()
        ret['significant_control'] = instance.get_significant_control_display()
        ret['cytotoxicity_observed'] = instance.get_cytotoxicity_observed_display()
        ret['precipitation_observed'] = instance.get_precipitation_observed_display()
        return ret

    class Meta:
        model = models.IVEndpointGroup


class IVBenchmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IVBenchmark


class IVEndpointCategory(serializers.ModelSerializer):

    def to_representation(self, instance):
        return OrderedDict(names=instance.get_list_representation())

    class Meta:
        model = models.IVEndpointCategory


class IVEndpointSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    chemical = _IVChemicalSerializer()
    experiment = IVExperimentSerializer()
    groups = IVEndpointGroupSerializer(many=True)
    benchmarks = IVBenchmarkSerializer(many=True)
    category = IVEndpointCategory()

    def to_representation(self, instance):
        ret = super(IVEndpointSerializer, self).to_representation(instance)
        ret['data_type'] = instance.get_data_type_display()
        ret['variance_type'] = instance.get_variance_type_display()
        ret['observation_time_units'] = instance.get_observation_time_units_display()
        ret['monotonicity'] = instance.get_monotonicity_display()
        ret['overall_pattern'] = instance.get_overall_pattern_display()
        ret['trend_test'] = instance.get_trend_test_display()
        ret['additional_fields'] = json.loads(instance.additional_fields)
        return ret

    class Meta:
        model = models.IVEndpoint
        depth = 1


SerializerHelper.add_serializer(models.IVEndpoint, IVEndpointSerializer)
