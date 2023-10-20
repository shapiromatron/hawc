from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ..assessment.models import DoseUnits
from ..assessment.serializers import (
    DoseUnitsSerializer,
    DSSToxSerializer,
    RelatedEffectTagSerializer,
)
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
        if not isinstance(data, str):
            raise serializers.ValidationError(f"'{data}' must be a string.")
        try:
            return models.Country.objects.get(code=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"'{data}' is not a country.")


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
    resulttags = RelatedEffectTagSerializer(required=False, many=True)
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

    def create(self, validated_data):
        resulttags = validated_data.pop("resulttags", [])
        instance = super().create(validated_data)
        instance.resulttags.set(resulttags)
        return instance

    def update(self, instance, validated_data):
        resulttags = validated_data.pop("resulttags", [])
        instance = super().update(instance, validated_data)
        # only modify if it was in request (don't change in a patch w/o this field)
        if "resulttags" in self.context["request"].data:
            instance.resulttags.set(resulttags)
        return instance


class OutcomeSerializer(IdLookupMixin, serializers.ModelSerializer):
    diagnostic = FlexibleChoiceField(choices=constants.Diagnostic.choices)
    study_population = StudyPopulationSerializer()
    can_create_sets = serializers.BooleanField(read_only=True)
    effects = RelatedEffectTagSerializer(required=False, many=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    results = ResultSerializer(many=True, read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True, read_only=True)

    class Meta:
        model = models.Outcome
        fields = "__all__"

    def create(self, validated_data):
        effects = validated_data.pop("effects", [])
        instance = super().create(validated_data)
        instance.effects.set(effects)
        return instance

    def update(self, instance, validated_data):
        effects = validated_data.pop("effects", [])
        instance = super().update(instance, validated_data)
        # only modify if it was in request (don't change in a patch w/o this field)
        if "effects" in self.context["request"].data:
            instance.effects.set(effects)
        return instance


class ComparisonSetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    exposure = ExposureSerializer(required=False)
    outcome = OutcomeSerializer(required=False)
    study_population = StudyPopulationSerializer(required=False)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"

    def validate(self, attrs):
        if self.instance is None:
            # make sure all provided objects (exposure, outcome, study population) are
            # from the same study and either study_population or outcome exists, but not both
            exposure = attrs.get("exposure")
            study_population = attrs.get("study_population")
            outcome = attrs.get("outcome")
            if (outcome is None and study_population is None) or (
                outcome is not None and study_population is not None
            ):
                raise serializers.ValidationError(
                    "Must supply either a study_population or an outcome, but not both"
                )
            if exposure and study_population:
                if exposure.get_study().id != study_population.get_study().id:
                    raise serializers.ValidationError(
                        "Supplied exposure and study_population are part of different studies."
                    )
            elif exposure and outcome:
                if exposure.get_study().id != outcome.get_study().id:
                    raise serializers.ValidationError(
                        "Supplied exposure and outcome are part of different studies."
                    )

        else:
            # When updating, validate that all related objects are part of the same study.
            study_id = self.instance.get_study().id
            if study_population := attrs.get("study_population"):
                if study_population.get_study().id != study_id:
                    raise serializers.ValidationError("Supplied study_population not study.")

            if exposure := attrs.get("exposure"):
                if exposure.get_study().id != study_id:
                    raise serializers.ValidationError("Supplied exposure not in study.")

            if outcome := attrs.get("outcome"):
                if outcome.get_study().id != study_id:
                    raise serializers.ValidationError("Supplied outcome not in study.")

        return super().validate(attrs)


class OutcomeCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Outcome
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.study_population.study.short_citation


class StudyPopulationCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.StudyPopulation
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class ExposureCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Exposure
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = (*cleanup_fields, "id")

    def get_study_short_citation(self, obj):
        return obj.study_population.study.short_citation


SerializerHelper.add_serializer(models.Outcome, OutcomeSerializer)
