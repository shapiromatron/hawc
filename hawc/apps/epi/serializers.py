from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ..assessment.models import DoseUnits
from ..assessment.serializers import DoseUnitsSerializer, DSSToxSerializer, EffectTagsSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..common.serializers import (
    FlexibleChoiceField,
    FlexibleDBLinkedChoiceField,
    GetOrCreateMixin,
    IdLookupMixin,
)
from ..study.serializers import StudySerializer
from . import constants, models


class EthnicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ethnicity
        fields = ("id", "name")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("name", "id")


class StudyPopulationCriteriaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="criteria.id")
    description = serializers.ReadOnlyField(source="criteria.description")
    criteria_type = serializers.CharField(source="get_criteria_type_display", read_only=True)

    class Meta:
        model = models.StudyPopulationCriteria
        fields = ("id", "description", "criteria_type")


class ExposureLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Exposure
        fields = ("id", "name", "url")


class StudyPopulationCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("code", "name")

    def to_internal_value(self, data):
        if type(data) is str:
            try:
                country = self.Meta.model.objects.get(code__iexact=data)
                return country
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"'{data}' is not a country.")

        return super().to_internal_value(data)


class OutcomeLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Outcome
        fields = ("id", "name", "url")


class GroupNumericalDescriptionsSerializer(serializers.ModelSerializer):
    mean_type = FlexibleChoiceField(choices=constants.GroupMeanType.choices)
    variance_type = FlexibleChoiceField(choices=constants.GroupVarianceType.choices)
    lower_type = FlexibleChoiceField(choices=constants.LowerLimit.choices)
    upper_type = FlexibleChoiceField(choices=constants.UpperLimit.choices)

    class Meta:
        model = models.GroupNumericalDescriptions
        fields = "__all__"


class GroupSerializer(IdLookupMixin, serializers.ModelSerializer):
    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    ethnicities = FlexibleDBLinkedChoiceField(models.Ethnicity, EthnicitySerializer, "name", True)
    descriptions = GroupNumericalDescriptionsSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Group
        fields = "__all__"


class ResultMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResultMetric
        fields = "__all__"


class CentralTendencySerializer(serializers.ModelSerializer):
    variance_type = FlexibleChoiceField(choices=constants.VarianceType.choices)
    estimate_type = FlexibleChoiceField(choices=constants.EstimateType.choices)
    lower_bound_interval = serializers.FloatField(read_only=True)
    upper_bound_interval = serializers.FloatField(read_only=True)

    class Meta:
        model = models.CentralTendency
        fields = "__all__"


class ComparisonSetLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.ComparisonSet
        fields = ("id", "name", "url")


class CriteriaSerializer(GetOrCreateMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Criteria
        fields = "__all__"


class SimpleStudyPopulationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudyPopulationCriteria
        fields = "__all__"


class StudyPopulationSerializer(IdLookupMixin, serializers.ModelSerializer):
    study = StudySerializer()
    criteria = StudyPopulationCriteriaSerializer(source="spcriteria", many=True, read_only=True)
    countries = StudyPopulationCountrySerializer(many=True)
    design = FlexibleChoiceField(choices=constants.Design.choices)
    outcomes = OutcomeLinkSerializer(many=True, read_only=True)
    exposures = ExposureLinkSerializer(many=True, read_only=True)
    can_create_sets = serializers.BooleanField(read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.StudyPopulation
        fields = "__all__"

    def update(self, instance, validated_data):
        if "countries" in validated_data:
            instance.countries.set(validated_data["countries"])
            # Delete the key so we can call the default update method for all the other fields.
            del validated_data["countries"]

        return super().update(instance, validated_data)

    def create(self, validated_data):
        countries = validated_data.pop("countries", None)
        instance = super().create(validated_data)
        if countries:
            instance.countries.set(countries)

        return instance


class ExposureSerializer(IdLookupMixin, serializers.ModelSerializer):
    dtxsid = DSSToxSerializer()
    study_population = StudyPopulationSerializer()
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    metric_units = DoseUnitsSerializer()
    central_tendencies = CentralTendencySerializer(many=True)

    class Meta:
        model = models.Exposure
        fields = "__all__"


class ExposureWriteSerializer(serializers.ModelSerializer):
    central_tendencies = CentralTendencySerializer(many=True, read_only=True)
    metric_units = FlexibleDBLinkedChoiceField(DoseUnits, DoseUnitsSerializer, "name", False)

    class Meta:
        model = models.Exposure
        fields = "__all__"


class GroupResultSerializer(serializers.ModelSerializer):
    main_finding_support = FlexibleChoiceField(choices=constants.MainFinding.choices)
    p_value_text = serializers.CharField(read_only=True)
    p_value_qualifier_display = serializers.CharField(
        source="get_p_value_qualifier_display", read_only=True
    )
    lower_bound_interval = serializers.FloatField(read_only=True)
    upper_bound_interval = serializers.FloatField(read_only=True)
    group = GroupSerializer()

    class Meta:
        model = models.GroupResult
        fields = "__all__"

    def validate(self, attrs):
        if self.instance is None:
            # When creating, we will validate that the supplied result and group (both required) are part of the same assessment.

            result = attrs["result"]
            group = attrs["group"]
            if result.get_assessment().id != group.get_assessment().id:
                raise serializers.ValidationError(
                    "Supplied result and group are part of different assessments."
                )
        else:
            # When updating, we will validate that the result and group (if either are present) are part
            # of the same assessment as the existing GroupResult object. (unless we think it'd ever be useful to allow someone
            # to create a GroupResult in one assessment with a given group/result, and later move it?)

            assessment_id = self.instance.get_assessment().id

            if "group" in attrs:
                group = attrs["group"]
                if group.get_assessment().id != assessment_id:
                    raise serializers.ValidationError("Supplied group is not in the assessment.")

            if "result" in attrs:
                result = attrs["result"]
                if result.get_assessment().id != assessment_id:
                    raise serializers.ValidationError("Supplied result is not in the assessment.")

        return super().validate(attrs)


class SimpleResultAdjustmentFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResultAdjustmentFactor
        fields = "__all__"


class ResultAdjustmentFactorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="adjustment_factor.id")
    description = serializers.ReadOnlyField(source="adjustment_factor.description")

    class Meta:
        model = models.ResultAdjustmentFactor
        fields = ("id", "description", "included_in_final_model")


class AdjustmentFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdjustmentFactor
        fields = "__all__"


class SimpleComparisonSetSerializer(IdLookupMixin, serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    exposure = ExposureSerializer()

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"


class ResultSerializer(serializers.ModelSerializer):
    dose_response = FlexibleChoiceField(choices=constants.DoseResponse.choices)
    metric = FlexibleDBLinkedChoiceField(
        models.ResultMetric, ResultMetricSerializer, "metric", False
    )
    statistical_power = FlexibleChoiceField(choices=constants.StatisticalPower.choices)
    estimate_type = FlexibleChoiceField(choices=constants.EstimateType.choices)
    variance_type = FlexibleChoiceField(choices=constants.VarianceType.choices)
    factors = ResultAdjustmentFactorSerializer(source="resfactors", many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    resulttags = EffectTagsSerializer(read_only=True)
    results = GroupResultSerializer(many=True, read_only=True)
    comparison_set = SimpleComparisonSetSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        models.GroupResult.getStdevs(ret["variance_type"], ret["results"])
        models.GroupResult.percentControl(
            ret["estimate_type"], ret["variance_type"], ret["results"]
        )
        models.GroupResult.getConfidenceIntervals(ret["variance_type"], ret["results"])
        return ret

    class Meta:
        model = models.Result
        exclude = ("adjustment_factors",)


class OutcomeSerializer(IdLookupMixin, serializers.ModelSerializer):
    diagnostic = FlexibleChoiceField(choices=constants.Diagnostic.choices)
    study_population = StudyPopulationSerializer()
    can_create_sets = serializers.BooleanField(read_only=True)
    effects = EffectTagsSerializer(read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    results = ResultSerializer(many=True, read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True, read_only=True)

    class Meta:
        model = models.Outcome
        fields = "__all__"


class ComparisonSetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    exposure = ExposureSerializer(required=False, allow_null=True)
    outcome = OutcomeSerializer(required=False, allow_null=True)
    study_population = StudyPopulationSerializer(required=False, allow_null=True)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"

    def validate(self, attrs):
        if self.instance is None:
            # make sure all provided values are from the same assessment
            # can provide either study population or outcome--but not both
            exposure = attrs.get("exposure", None)
            study_population = attrs.get("study_population", None)
            outcome = attrs.get("outcome", None)
            if exposure and study_population:
                if exposure.get_assessment().id != study_population.get_assessment().id:
                    raise serializers.ValidationError(
                        "Supplied exposure and study_population are part of different assessments."
                    )
            elif exposure and outcome:
                if exposure.get_assessment().id != outcome.get_assessment().id:
                    raise serializers.ValidationError(
                        "Supplied exposure and outcome are part of different assessments."
                    )
            if outcome and study_population:
                raise serializers.ValidationError(
                    "Cannot create a comparison set with both an outcome and study_population"
                )
            if outcome is None and study_population is None:
                raise serializers.ValidationError("Must supply either study_population or outcome")

        else:
            # When updating, we will validate that the exposure and study_population (if either are present) are part
            # of the same assessment as the existing ComparisonSet object. (unless we think it'd ever be useful to allow someone
            # to create a ComparisonSet in one assessment with a given study_population/exposure, and later move it?)

            assessment_id = self.instance.get_assessment().id

            if "study_population" in attrs:
                study_population = attrs["study_population"]
                if study_population.get_assessment().id != assessment_id:
                    raise serializers.ValidationError(
                        "Supplied study_population is not in the assessment."
                    )

            if "exposure" in attrs:
                exposure = attrs["exposure"]
                if exposure.get_assessment().id != assessment_id:
                    raise serializers.ValidationError("Supplied exposure is not in the assessment.")

            if "outcome" in attrs:
                outcome = attrs["outcome"]
                if outcome.get_assessment().id != assessment_id:
                    raise serializers.ValidationError("Supplied outcome is not in the assessment.")

        return super().validate(attrs)


class OutcomeCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Outcome
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.study_population.study.short_citation


class StudyPopulationCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.StudyPopulation
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class ExposureCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Exposure
        cleanup_fields = ("study_short_citation",) + model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)

    def get_study_short_citation(self, obj):
        return obj.study_population.study.short_citation


SerializerHelper.add_serializer(models.Outcome, OutcomeSerializer)
