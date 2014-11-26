from rest_framework import serializers

from study.serializers import StudySerializer

from utils.helper import SerializerHelper

from . import models


class StudyCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StudyCriteria
        depth = 0


class EthnicitySerializer(serializers.ModelSerializer):

    def transform_ethnicity(self, obj, value):
        return obj.get_ethnicity_display()

    class Meta:
        model = models.Ethnicity
        depth = 0


class FactorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Factor
        depth = 0


class StudyPopulationSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    study = StudySerializer()
    ethnicity = EthnicitySerializer()
    inclusion_criteria = StudyCriteriaSerializer()
    exclusion_criteria = StudyCriteriaSerializer()
    confounding_criteria = StudyCriteriaSerializer()

    def transform_design(self, obj, value):
        return obj.get_design_display()

    def transform_country(self, obj, value):
        return obj.get_country_display()

    def transform_sex(self, obj, value):
        return obj.get_sex_display()

    def transform_age_sd_type(self, obj, value):
        return obj.get_age_sd_type_display()

    def transform_age_mean_type(self, obj, value):
        return obj.get_age_mean_type_display()

    def transform_age_lower_type(self, obj, value):
        return obj.get_age_lower_type_display()

    def transform_age_upper_type(self, obj, value):
        return obj.get_age_upper_type_display()

    class Meta:
        model = models.StudyPopulation


class ExposureSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    study_population = StudyPopulationSerializer()

    class Meta:
        model = models.Exposure
        depth = 1


class ExposureGroupSerializer(serializers.ModelSerializer):
    ethnicity = EthnicitySerializer()

    def transform_sex(self, obj, value):
        return obj.get_sex_display()

    def transform_age_sd_type(self, obj, value):
        return obj.get_age_sd_type_display()

    def transform_age_mean_type(self, obj, value):
        return obj.get_age_mean_type_display()

    def transform_age_lower_type(self, obj, value):
        return obj.get_age_lower_type_display()

    def transform_age_upper_type(self, obj, value):
        return obj.get_age_upper_type_display()

    class Meta:
        model = models.ExposureGroup


class AssessedOutcomeGroupSerializer(serializers.ModelSerializer):
    assessed_outcome = serializers.PrimaryKeyRelatedField()
    exposure_group = ExposureGroupSerializer()
    p_value_text = serializers.CharField(source='p_value_text', read_only=True)
    isMainFinding = serializers.CharField(source='isMainFinding', read_only=True)

    class Meta:
        model = models.AssessedOutcomeGroup


class AssessedOutcomeSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    assessment = serializers.PrimaryKeyRelatedField()
    exposure = ExposureSerializer()
    groups = AssessedOutcomeGroupSerializer(many=True)
    main_finding = serializers.PrimaryKeyRelatedField()
    adjustment_factors = FactorSerializer()
    confounders_considered = FactorSerializer()

    def transform_diagnostic(self, obj, value):
        return obj.get_diagnostic_display()

    def transform_dose_response(self, obj, value):
        return obj.get_dose_response_display()

    def transform_statistical_power(self, obj, value):
        return obj.get_statistical_power_display()

    def transform_main_finding_support(self, obj, value):
        return obj.get_main_finding_support_display()

    class Meta:
        model = models.AssessedOutcome
        depth = 1


class AssessedOutcomeShallowSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = models.AssessedOutcome
        depth = 0


class AssessedOutcomeGroupVerboseSerializer(serializers.ModelSerializer):
    assessed_outcome = AssessedOutcomeShallowSerializer()

    class Meta:
        model = models.AssessedOutcomeGroup
        depth = 0


class SingleResultSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    outcome_group = AssessedOutcomeGroupVerboseSerializer()
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


class MetaResultSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    protocol = MetaProtocolSerializer()
    adjustment_factors = FactorSerializer()
    single_results = SingleResultSerializer(many=True)

    class Meta:
        model = models.MetaResult
        depth = 4



SerializerHelper.add_serializer(models.StudyPopulation, StudyPopulationSerializer)
SerializerHelper.add_serializer(models.AssessedOutcome, AssessedOutcomeSerializer)
SerializerHelper.add_serializer(models.MetaProtocol, MetaProtocolSerializer)
SerializerHelper.add_serializer(models.MetaResult, MetaResultSerializer)
