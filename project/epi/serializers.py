from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer
from study.serializers import StudySerializer

from utils.helper import SerializerHelper

from . import models


class StudyCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StudyCriteria


class StatisticalMetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StatisticalMetric


class StudyPopulationSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    ethnicity = serializers.StringRelatedField(many=True)
    inclusion_criteria = serializers.StringRelatedField(many=True)
    exclusion_criteria = serializers.StringRelatedField(many=True)
    confounding_criteria = serializers.StringRelatedField(many=True)

    def to_representation(self, instance):
        ret = super(StudyPopulationSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['design'] = instance.get_design_display()
        ret['country'] = instance.get_country_display()
        ret['sex'] = instance.get_sex_display()
        ret['age_sd_type'] = instance.get_age_sd_type_display()
        ret['age_mean_type'] = instance.get_age_mean_type_display()
        ret['age_lower_type'] = instance.get_age_lower_type_display()
        ret['age_upper_type'] = instance.get_age_upper_type_display()
        return ret

    class Meta:
        model = models.StudyPopulation


class ExposureSerializer(serializers.ModelSerializer):
    study_population = StudyPopulationSerializer()

    def to_representation(self, instance):
        ret = super(ExposureSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Exposure
        depth = 1


class ExposureGroupSerializer(serializers.ModelSerializer):
    ethnicity = serializers.StringRelatedField(many=True)

    def to_representation(self, instance):
        ret = super(ExposureGroupSerializer, self).to_representation(instance)
        ret['sex'] = instance.get_sex_display()
        ret['age_sd'] = instance.get_age_sd_type_display()
        ret['age_mean_type'] = instance.get_age_mean_type_display()
        ret['age_lower_type'] = instance.get_age_lower_type_display()
        ret['age_upper_type'] = instance.get_age_upper_type_display()
        return ret

    class Meta:
        model = models.ExposureGroup


class AssessedOutcomeGroupSerializer(serializers.ModelSerializer):
    assessed_outcome = serializers.PrimaryKeyRelatedField(read_only=True)
    exposure_group = ExposureGroupSerializer()

    def to_representation(self, instance):
        ret = super(AssessedOutcomeGroupSerializer, self).to_representation(instance)
        ret['p_value_text'] = instance.p_value_text
        ret['isMainFinding'] = instance.isMainFinding
        return ret

    class Meta:
        model = models.AssessedOutcomeGroup


class AssessedOutcomeSerializer(serializers.ModelSerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    main_finding = serializers.PrimaryKeyRelatedField(read_only=True)
    exposure = ExposureSerializer()
    statistical_metric = StatisticalMetricSerializer()
    effects = EffectTagsSerializer()
    groups = AssessedOutcomeGroupSerializer(many=True)
    adjustment_factors = serializers.StringRelatedField(many=True)
    confounders_considered = serializers.StringRelatedField(many=True)

    def to_representation(self, instance):
        ret = super(AssessedOutcomeSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['diagnostic'] = instance.get_diagnostic_display()
        ret['dose_response'] = instance.get_dose_response_display()
        ret['statistical_power'] = instance.get_statistical_power_display()
        ret['main_finding_support'] = instance.get_main_finding_support_display()
        return ret

    class Meta:
        model = models.AssessedOutcome


class AssessedOutcomeShallowSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(AssessedOutcomeShallowSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.AssessedOutcome


class AssessedOutcomeGroupVerboseSerializer(serializers.ModelSerializer):
    assessed_outcome = AssessedOutcomeShallowSerializer()

    class Meta:
        model = models.AssessedOutcomeGroup


class SingleResultSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    outcome_group = AssessedOutcomeGroupVerboseSerializer()
    meta_result = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.SingleResult


class MetaProtocolSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    inclusion_criteria = serializers.StringRelatedField(many=True)
    exclusion_criteria = serializers.StringRelatedField(many=True)

    def to_representation(self, instance):
        ret = super(MetaProtocolSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        ret['protocol_type'] = instance.get_protocol_type_display()
        ret['lit_search_strategy'] = instance.get_lit_search_strategy_display()
        return ret

    class Meta:
        model = models.MetaProtocol


class MetaResultSerializer(serializers.ModelSerializer):
    protocol = MetaProtocolSerializer()
    statistical_metric = StatisticalMetricSerializer()
    single_results = SingleResultSerializer(many=True)
    adjustment_factors = serializers.StringRelatedField(many=True)

    def to_representation(self, instance):
        ret = super(MetaResultSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.MetaResult


SerializerHelper.add_serializer(models.StudyPopulation, StudyPopulationSerializer)
SerializerHelper.add_serializer(models.AssessedOutcome, AssessedOutcomeSerializer)
SerializerHelper.add_serializer(models.MetaProtocol, MetaProtocolSerializer)
SerializerHelper.add_serializer(models.MetaResult, MetaResultSerializer)
