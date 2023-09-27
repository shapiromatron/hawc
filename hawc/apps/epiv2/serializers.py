from django.db import transaction
from rest_framework import serializers

from ..assessment.models import DSSTox
from ..assessment.serializers import DSSToxSerializer
from ..common.api import DynamicFieldsMixin
from ..common.serializers import FlexibleChoiceArrayField, FlexibleChoiceField, IdLookupMixin
from ..epi.serializers import StudyPopulationCountrySerializer
from ..study.models import Study
from ..study.serializers import StudySerializer
from . import constants, mixins, models


class ChemicalSerializer(serializers.ModelSerializer):
    dsstox_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="dsstox",
        queryset=DSSTox.objects.all(),
        required=False,
        allow_null=True,
    )
    dsstox = DSSToxSerializer(read_only=True)

    class Meta:
        model = models.Chemical
        fields = ["id", "design", "name", "dsstox_id", "dsstox"]


class ExposureSerializer(serializers.ModelSerializer):
    exposure_route = FlexibleChoiceField(choices=constants.ExposureRoute.choices)
    biomonitoring_matrix = FlexibleChoiceField(
        choices=constants.BiomonitoringMatrix.choices, allow_blank=True
    )
    biomonitoring_source = FlexibleChoiceField(
        choices=constants.BiomonitoringSource.choices, allow_blank=True
    )

    class Meta:
        model = models.Exposure
        exclude = ["created", "last_updated"]


class ExposureLevelSerializer(mixins.SameDesignSerializerMixin, serializers.ModelSerializer):
    variance_type = FlexibleChoiceField(choices=constants.VarianceType.choices)
    ci_type = FlexibleChoiceField(choices=constants.ConfidenceIntervalType.choices)

    chemical_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="chemical",
        queryset=models.Chemical.objects.all(),
        required=True,
        allow_null=False,
    )
    chemical = ChemicalSerializer(read_only=True)
    exposure_measurement_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="exposure_measurement",
        queryset=models.Exposure.objects.all(),
        required=True,
        allow_null=False,
    )
    exposure_measurement = ExposureSerializer(read_only=True)

    same_design_fields = [
        ("chemical_id", models.Chemical),
        ("exposure_measurement_id", models.Exposure),
    ]

    class Meta:
        model = models.ExposureLevel
        exclude = ["created", "last_updated"]


class OutcomeSerializer(serializers.ModelSerializer):
    system = FlexibleChoiceField(choices=constants.HealthOutcomeSystem.choices)

    class Meta:
        model = models.Outcome
        exclude = ["created", "last_updated"]


class AdjustmentFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdjustmentFactor
        exclude = ["created", "last_updated"]


class DataExtractionSerializer(mixins.SameDesignSerializerMixin, serializers.ModelSerializer):
    ci_type = FlexibleChoiceField(choices=constants.ConfidenceIntervalType.choices)
    variance_type = FlexibleChoiceField(choices=constants.VarianceType.choices)
    significant = FlexibleChoiceField(choices=constants.Significant.choices)
    adverse_direction = FlexibleChoiceField(choices=constants.AdverseDirection.choices)

    outcome_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="outcome",
        queryset=models.Outcome.objects.all(),
        required=True,
        allow_null=False,
    )
    outcome = OutcomeSerializer(read_only=True)

    exposure_level_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="exposure_level",
        queryset=models.ExposureLevel.objects.all(),
        required=True,
        allow_null=False,
    )
    exposure_level = ExposureLevelSerializer(read_only=True)

    factors_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="factors",
        queryset=models.AdjustmentFactor.objects.all(),
        required=False,
        allow_null=True,
    )
    factors = AdjustmentFactorSerializer(read_only=True)

    same_design_fields = [
        ("outcome_id", models.Outcome),
        ("exposure_level_id", models.ExposureLevel),
        ("factors_id", models.AdjustmentFactor),
    ]

    class Meta:
        model = models.DataExtraction
        exclude = ["created", "last_updated"]


class DesignSerializer(IdLookupMixin, serializers.ModelSerializer):
    study_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="study",
        queryset=Study.objects.all(),
        required=True,
        allow_null=False,
    )
    study = StudySerializer(read_only=True)

    study_design = FlexibleChoiceField(choices=constants.StudyDesign.choices)
    age_profile = FlexibleChoiceArrayField(choices=constants.AgeProfile.choices)
    source = FlexibleChoiceField(choices=constants.Source.choices)
    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    countries = StudyPopulationCountrySerializer(many=True)
    chemicals = ChemicalSerializer(many=True, read_only=True)
    exposures = ExposureSerializer(many=True, read_only=True)
    exposure_levels = ExposureLevelSerializer(many=True, read_only=True)
    outcomes = OutcomeSerializer(many=True, read_only=True)
    adjustment_factors = AdjustmentFactorSerializer(many=True, read_only=True)
    data_extractions = DataExtractionSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    nested_models = ["countries"]

    class Meta:
        model = models.Design
        exclude = ["created", "last_updated"]

    @transaction.atomic
    def create(self, validated_data):
        if "age_profile" not in validated_data:
            validated_data["age_profile"] = []

        nested_validated_data = {}

        # remove nested models from validated_data
        for model in self.nested_models:
            data = validated_data.pop(model, None)
            nested_validated_data.update({model: data})

        # execute inherited create method
        instance = super().create(validated_data)

        # add nested models to the instance
        if countries := nested_validated_data.get("countries"):
            instance.countries.set(countries)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        nested_validated_data = {}

        # remove nested models from validated_data
        for model in self.nested_models:
            data = validated_data.pop(model, None)
            nested_validated_data.update({model: data})

        # execute inherited create method
        instance = super().update(instance, validated_data)

        # add nested models to the instance
        if countries := nested_validated_data.get("countries"):
            instance.countries.set(countries)

        return instance


class DesignCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Design
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class ChemicalCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Chemical
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation


class ExposureCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Exposure
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation


class ExposureLevelCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.ExposureLevel
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation


class OutcomeCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Outcome
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation


class AdjustmentFactorCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.AdjustmentFactor
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation


class DataExtractionCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.DataExtraction
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation
