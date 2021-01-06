from rest_framework import serializers
from hawc.apps.animal import models
from hawc.apps.assessment.models import Species, Strain, DoseUnits
from hawc.apps.common.actions import BaseApiAction
from pydantic import BaseModel


def tuple_to_dict(tuple):
    return {e[0]: e[1] for e in tuple}


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ("id", "name")


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = ("id", "species_id", "name")


class DoseUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoseUnits
        fields = ("id", "name")


class NoInput(BaseModel):
    pass


class AnimalMetadata(BaseApiAction):
    input_model = NoInput

    def experiment_metadata(self):
        metadata = {}
        metadata["type"] = tuple_to_dict(models.Experiment.EXPERIMENT_TYPE_CHOICES)
        return metadata

    def animal_group_metadata(self):
        metadata = {}
        species = Species.objects.all()
        strains = Strain.objects.all()
        metadata["sex"] = models.AnimalGroup.SEX_DICT
        metadata["generation"] = models.AnimalGroup.GENERATION_DICT
        metadata["species"] = SpeciesSerializer(species, many=True).data
        metadata["strains"] = StrainSerializer(strains, many=True).data
        metadata["lifestage"] = tuple_to_dict(models.AnimalGroup.LIFESTAGE_CHOICES)
        return metadata

    def dosing_regime_metadata(self):
        metadata = {}
        metadata["route_of_exposure"] = models.DosingRegime.ROUTE_EXPOSURE_CHOICES_DICT
        metadata["positive_control"] = tuple_to_dict(models.DosingRegime.POSITIVE_CONTROL_CHOICES)
        metadata["negative_control"] = tuple_to_dict(models.DosingRegime.NEGATIVE_CONTROL_CHOICES)
        return metadata

    def dose_group_metadata(self):
        metadata = {}
        dose_units = DoseUnits.objects.all()
        metadata["dose_units"] = DoseUnitsSerializer(dose_units, many=True).data
        return metadata

    def endpoint_metadata(self):
        metadata = {}
        metadata["litter_effects"] = tuple_to_dict(models.Endpoint.LITTER_EFFECT_CHOICES)
        metadata["observation_time_units"] = tuple_to_dict(models.Endpoint.OBSERVATION_TIME_UNITS)
        metadata["adversity_direction"] = tuple_to_dict(models.Endpoint.ADVERSE_DIRECTION_CHOICES)
        metadata["data_type"] = tuple_to_dict(models.Endpoint.DATA_TYPE_CHOICES)
        metadata["variance_type"] = tuple_to_dict(models.Endpoint.VARIANCE_TYPE_CHOICES)
        metadata["monotonicity"] = tuple_to_dict(models.Endpoint.MONOTONICITY_CHOICES)
        metadata["trend_result"] = tuple_to_dict(models.Endpoint.TREND_RESULT_CHOICES)
        return metadata

    def evaluate(self):
        metadata = {}
        metadata["experiment"] = self.experiment_metadata()
        metadata["animal_group"] = self.animal_group_metadata()
        metadata["dosing_regime"] = self.dosing_regime_metadata()
        metadata["dose_group"] = self.dose_group_metadata()
        metadata["endpoint"] = self.endpoint_metadata()
        return metadata
