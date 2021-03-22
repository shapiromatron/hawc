from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ..assessment.serializers import DoseUnitsSerializer, DSSToxSerializer, EffectTagsSerializer
from ..common.api import DynamicFieldsMixin, GetOrCreateMixin, IdLookupMixin
from ..common.helper import SerializerHelper
from ..common.serializers import FlexibleChoiceField, FlexibleDBLinkedChoiceField
from ..study.serializers import StudySerializer
from . import forms, models


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
                raise serializers.ValidationError(f"Invalid country code '{data}'")

        return super().to_internal_value(data)


class OutcomeLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Outcome
        fields = ("id", "name", "url")


class GroupNumericalDescriptionsSerializer(serializers.ModelSerializer):
    form_integration_class = forms.GroupNumericalDescriptionsForm

    mean_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.MEAN_TYPE_CHOICES)
    variance_type = FlexibleChoiceField(
        choices=models.GroupNumericalDescriptions.VARIANCE_TYPE_CHOICES
    )
    lower_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.LOWER_LIMIT_CHOICES)
    upper_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.UPPER_LIMIT_CHOICES)

    class Meta:
        model = models.GroupNumericalDescriptions
        # exclude = ("group",)
        fields = "__all__"


class GroupSerializer(IdLookupMixin, serializers.ModelSerializer):
    form_integration_class = forms.GroupForm

    sex = FlexibleChoiceField(choices=models.Group.SEX_CHOICES)
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
    variance_type = serializers.CharField(source="get_variance_type_display", read_only=True)
    estimate_type = serializers.CharField(source="get_estimate_type_display", read_only=True)
    lower_bound_interval = serializers.FloatField(read_only=True)
    upper_bound_interval = serializers.FloatField(read_only=True)

    class Meta:
        model = models.CentralTendency
        fields = "__all__"


class CentralTendencyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CentralTendency
        fields = "__all__"


class CentralTendencyPreviewSerializer(serializers.ModelSerializer):
    """
    CT serializer that doesn't require "exposure" - can be used blahblah
    """

    class Meta:
        model = models.CentralTendency
        exclude = ("exposure",)


class ComparisonSetLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.ComparisonSet
        fields = ("id", "name", "url")


class CriteriaSerializer(GetOrCreateMixin, serializers.ModelSerializer):
    form_integration_class = forms.CriteriaForm

    def get_form_integration_kwargs(self, data):
        return {"parent": data["assessment"]}

    class Meta:
        model = models.Criteria
        fields = "__all__"


class SimpleStudyPopulationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudyPopulationCriteria
        fields = "__all__"


class StudyPopulationSerializer(IdLookupMixin, serializers.ModelSerializer):
    form_integration_class = forms.StudyPopulationForm

    study = StudySerializer()
    criteria = StudyPopulationCriteriaSerializer(source="spcriteria", many=True, read_only=True)
    countries = StudyPopulationCountrySerializer(many=True)
    design = FlexibleChoiceField(choices=models.StudyPopulation.DESIGN_CHOICES)
    outcomes = OutcomeLinkSerializer(many=True, read_only=True)
    exposures = ExposureLinkSerializer(many=True, read_only=True)
    can_create_sets = serializers.BooleanField(read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    def get_form_integration_kwargs(self, data):
        return {"parent": data["study"]}

    class Meta:
        model = models.StudyPopulation
        fields = "__all__"

    def update(self, instance, validated_data):
        if "countries" in validated_data:
            instance.countries.clear()
            instance.countries.add(*validated_data["countries"])
            del validated_data[
                "countries"
            ]  # delete the key so we can call the default update method for all the other fields

        return super().update(instance, validated_data)

    def create(self, validated_data):
        temp_countries = None
        if "countries" in validated_data:
            temp_countries = validated_data["countries"]
            del validated_data[
                "countries"
            ]  # delete the key so we can call the default update method for all the other fields
        instance = super().create(validated_data)

        if temp_countries is not None:
            instance.countries.add(*temp_countries)
            instance.save()

        return instance


class SimpleExposureSerializer(IdLookupMixin, serializers.ModelSerializer):
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
    form_integration_class = forms.ExposureForm

    class Meta:
        model = models.Exposure
        fields = "__all__"


class GroupResultSerializer(serializers.ModelSerializer):
    form_integration_class = forms.GroupResultForm

    main_finding_support = FlexibleChoiceField(choices=models.GroupResult.MAIN_FINDING_CHOICES)
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
    exposure = SimpleExposureSerializer()

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"


class ResultSerializer(serializers.ModelSerializer):
    form_integration_class = forms.ResultForm

    dose_response = FlexibleChoiceField(choices=models.Result.DOSE_RESPONSE_CHOICES)
    metric = FlexibleDBLinkedChoiceField(
        models.ResultMetric, ResultMetricSerializer, "metric", False
    )
    statistical_power = FlexibleChoiceField(choices=models.Result.STATISTICAL_POWER_CHOICES)
    estimate_type = FlexibleChoiceField(choices=models.Result.ESTIMATE_TYPE_CHOICES)
    variance_type = FlexibleChoiceField(choices=models.Result.VARIANCE_TYPE_CHOICES)
    factors = ResultAdjustmentFactorSerializer(source="resfactors", many=True, read_only=True)
    # factors_applied = AdjustmentFactorSerializer(many=True, read_only=True)
    # factors_considered = AdjustmentFactorSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    resulttags = EffectTagsSerializer(read_only=True)
    results = GroupResultSerializer(many=True, read_only=True)
    comparison_set = SimpleComparisonSetSerializer()

    def get_form_integration_kwargs(self, data):
        return {"parent": data["outcome"]}

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
        # fields = "__all__"
        exclude = ("adjustment_factors",)


class OutcomeSerializer(serializers.ModelSerializer):
    form_integration_class = forms.OutcomeForm

    diagnostic = FlexibleChoiceField(choices=models.Outcome.DIAGNOSTIC_CHOICES)
    study_population = StudyPopulationSerializer()  # read_only=True)
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
    exposure = SimpleExposureSerializer()
    outcome = OutcomeSerializer(read_only=True)
    study_population = StudyPopulationSerializer()
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"


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
