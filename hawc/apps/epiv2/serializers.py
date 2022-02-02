from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from ..epi.serializers import StudyPopulationCountrySerializer
from ..study.serializers import StudySerializer
from . import constants, models


class AgeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AgeProfile
        fields = ["name"]

    def to_internal_value(self, data):
        if type(data) is str:
            try:
                age_profile = self.Meta.model.objects.get(name__iexact=data)
                return age_profile
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"'{data}' is not a valid Age profile.")

        return super().to_internal_value(data)


class MeasurementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeasurementType
        fields = ["description"]


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chemical
        fields = ["id", "name", "dsstox"]


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Criteria
        fields = ["id", "name"]


class ExposureSerializer(serializers.ModelSerializer):
    measurement_type = MeasurementTypeSerializer(many=True, read_only=True)
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
    study = StudySerializer()
    study_design = FlexibleChoiceField(choices=constants.StudyDesign.choices)
    source = FlexibleChoiceField(choices=constants.Source.choices)
    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    countries = StudyPopulationCountrySerializer(many=True)
    age_profile = AgeProfileSerializer(many=True)
    chemicals = ChemicalSerializer(many=True, read_only=True)
    criteria = CriteriaSerializer(many=True, read_only=True)
    exposure = ExposureSerializer(many=True, read_only=True)
    exposure_levels = ExposureLevelSerializer(many=True, read_only=True)
    outcomes = OutcomeSerializer(many=True, read_only=True)
    adjustment_factors = AdjustmentFactorSerializer(many=True, read_only=True)
    data_extractions = DataExtractionSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    def create(self, validated_data):
        nested_models = [
            "countries",
            "age_profile",
            # "chemicals",
            # "criteria",
            # "exposure",
            # "exposure_levels",
            # "outcomes",
            # "adjustment_factors",
            # "data_extractions",
        ]

        nested_validated_data = {}

        # remove nested models from validated_data
        for model in nested_models:
            data = validated_data.pop(model, None)
            nested_validated_data.update({model: data})

        # execute inherited create method
        instance = super().create(validated_data)

        # add nested models to the instance
        data = nested_validated_data.get("countries")
        if data:
            instance.countries.set(data),

        data = nested_validated_data.get("age_profile")
        if data:
            instance.age_profile.set(data),

        # data = nested_validated_data.get("chemicals")
        # if data:
        #     instance.chemicals.set(data),

        # data = nested_validated_data.get("criteria")
        # if data:
        #     instance.criteria.set(data),

        # data = nested_validated_data.get("exposure")
        # if data:
        #     instance.exposure.set(data),

        # data = nested_validated_data.get("exposure_levels")
        # if data:
        #     instance.exposure_levels.set(data),

        # data = nested_validated_data.get("outcomes")
        # if data:
        #     instance.outcomes.set(data),

        # data = nested_validated_data.get("adjustment_factors")
        # if data:
        #     instance.adjustment_factors.set(data),

        # data = nested_validated_data.get("data_extractions")
        # if data:
        #     instance.data_extractions.set(data),

        return instance

    class Meta:
        model = models.Design
        fields = "__all__"
