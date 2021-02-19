from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from ..assessment.models import Assessment
from ..assessment.serializers import DoseUnitsSerializer, DSSToxSerializer, EffectTagsSerializer
from ..common.api import DynamicFieldsMixin, GetOrCreateMixin, user_can_edit_object
from ..common.helper import SerializerHelper
from ..common.serializers import FlexibleChoiceField, FlexibleDBLinkedChoiceManyField
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


class OutcomeLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Outcome
        fields = ("id", "name", "url")


class GroupNumericalDescriptionsSerializer(serializers.ModelSerializer):
    mean_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.MEAN_TYPE_CHOICES)
    variance_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.VARIANCE_TYPE_CHOICES)
    lower_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.LOWER_LIMIT_CHOICES)
    upper_type = FlexibleChoiceField(choices=models.GroupNumericalDescriptions.UPPER_LIMIT_CHOICES)

    class Meta:
        model = models.GroupNumericalDescriptions
        # exclude = ("group",)
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    sex = FlexibleChoiceField(choices=models.Group.SEX_CHOICES)
    ethnicities = FlexibleDBLinkedChoiceManyField(models.Ethnicity, EthnicitySerializer, "name")
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


class SimpleExposureSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    metric_units = DoseUnitsSerializer()
    central_tendencies = CentralTendencySerializer(many=True)

    class Meta:
        model = models.Exposure
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


# class StudyPopulationSerializer(GetOrCreateMixin, serializers.ModelSerializer):
class StudyPopulationSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    criteria = StudyPopulationCriteriaSerializer(source="spcriteria", many=True)
    outcomes = OutcomeLinkSerializer(many=True)
    exposures = ExposureLinkSerializer(many=True)
    can_create_sets = serializers.BooleanField(read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True)
    countries = StudyPopulationCountrySerializer(many=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    design = serializers.CharField(source="get_design_display", read_only=True)

    class Meta:
        model = models.StudyPopulation
        fields = "__all__"

    def to_internal_value(self, data):
        if type(data) is int:
            try:
                study_pop = self.Meta.model.objects.get(id=data)
                return study_pop
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Invalid id")

        return data


class ExposureReadSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        data = super().validate(data)

        form = forms.ExposureForm(data=data)
        if form.is_valid() is False:
            raise serializers.ValidationError(form.errors)

        return data

    class Meta:
        model = models.Exposure
        fields = "__all__"


class GroupResultSerializer(serializers.ModelSerializer):
    main_finding_support = serializers.CharField(
        source="get_main_finding_support_display", read_only=True
    )
    p_value_qualifier = serializers.CharField(
        source="get_p_value_qualifier_display", read_only=True
    )
    p_value_text = serializers.CharField(read_only=True)
    lower_bound_interval = serializers.FloatField(read_only=True)
    upper_bound_interval = serializers.FloatField(read_only=True)
    group = GroupSerializer()

    class Meta:
        model = models.GroupResult
        fields = "__all__"


class ResultAdjustmentFactorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="adjustment_factor.id")
    description = serializers.ReadOnlyField(source="adjustment_factor.description")

    class Meta:
        model = models.ResultAdjustmentFactor
        fields = ("id", "description", "included_in_final_model")


class SimpleComparisonSetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    exposure = SimpleExposureSerializer()

    class Meta:
        model = models.ComparisonSet
        fields = "__all__"


class ResultReadSerializer(serializers.ModelSerializer):
    metric = ResultMetricSerializer()
    factors = ResultAdjustmentFactorSerializer(source="resfactors", many=True)
    dose_response = serializers.CharField(source="get_dose_response_display", read_only=True)
    statistical_power = serializers.CharField(
        source="get_statistical_power_display", read_only=True
    )
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    results = GroupResultSerializer(many=True)
    resulttags = EffectTagsSerializer()
    variance_type = serializers.CharField(source="get_variance_type_display", read_only=True)
    estimate_type = serializers.CharField(source="get_estimate_type_display", read_only=True)
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


class ResultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Result
        fields = "__all__"


class OutcomeSerializer(serializers.ModelSerializer):
    diagnostic = FlexibleChoiceField(choices=models.Outcome.DIAGNOSTIC_CHOICES)
    study_population = StudyPopulationSerializer(read_only=True)
    can_create_sets = serializers.BooleanField(read_only=True)
    effects = EffectTagsSerializer(read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    results = ResultReadSerializer(many=True, read_only=True)
    comparison_sets = ComparisonSetLinkSerializer(many=True, read_only=True)

    def validate(self, data):
        data = super().validate(data)

        form = forms.OutcomeForm(data=data)
        if form.is_valid() is False:
            raise serializers.ValidationError(form.errors)

        return data

    class Meta:
        model = models.Outcome
        fields = "__all__"



class ComparisonSetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    exposure = ExposureReadSerializer(read_only=True)
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
