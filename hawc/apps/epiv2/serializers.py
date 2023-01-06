from django.db import transaction
from rest_framework import serializers

from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from ..epi.serializers import StudyPopulationCountrySerializer
from ..study.serializers import VerboseStudySerializer
from . import constants, models


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chemical
        fields = ["id", "name", "dsstox"]


class ExposureSerializer(serializers.ModelSerializer):
    exposure_route = FlexibleChoiceField(choices=constants.ExposureRoute.choices)

    class Meta:
        model = models.Exposure
        exclude = ["design", "created", "last_updated"]


class ExposureLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExposureLevel
        exclude = ["design", "created", "last_updated"]


class OutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Outcome
        exclude = ["design", "created", "last_updated"]


class AdjustmentFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdjustmentFactor
        exclude = ["design", "created", "last_updated"]


class DataExtractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataExtraction
        exclude = ["design", "created", "last_updated"]


class DesignSerializer(IdLookupMixin, serializers.ModelSerializer):
    study = VerboseStudySerializer()
    study_design = FlexibleChoiceField(choices=constants.StudyDesign.choices)
    source = FlexibleChoiceField(choices=constants.Source.choices)
    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    countries = StudyPopulationCountrySerializer(many=True)
    chemicals = ChemicalSerializer(many=True, read_only=True)
    exposure = ExposureSerializer(many=True, read_only=True)
    exposure_levels = ExposureLevelSerializer(many=True, read_only=True)
    outcomes = OutcomeSerializer(many=True, read_only=True)
    adjustment_factors = AdjustmentFactorSerializer(many=True, read_only=True)
    data_extractions = DataExtractionSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        nested_models = [
            "countries",
        ]

        if "age_profile" not in validated_data:
            validated_data["age_profile"] = []

        nested_validated_data = {}

        # remove nested models from validated_data
        for model in nested_models:
            data = validated_data.pop(model, None)
            nested_validated_data.update({model: data})

        # execute inherited create method
        instance = super().create(validated_data)

        # add nested models to the instance
        if countries := nested_validated_data.get("countries"):
            instance.countries.set(countries)

        return instance

    class Meta:
        model = models.Design
        fields = "__all__"
