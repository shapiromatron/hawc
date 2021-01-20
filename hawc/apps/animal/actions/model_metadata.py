from pydantic import BaseModel

from hawc.apps.animal import models
from hawc.apps.assessment.models import DoseUnits, Species, Strain
from hawc.apps.common.actions import BaseApiAction
from hawc.apps.study.models import Study


def tuple_to_dict(tuple):
    return {e[0]: e[1] for e in tuple}


class NoInput(BaseModel):
    pass


class AnimalMetadata(BaseApiAction):
    """
    Generate a dictionary of field choices for all animal models.
    """

    input_model = NoInput

    def study_metadata(self):
        return dict(coi_reported=tuple_to_dict(Study.COI_REPORTED_CHOICES))

    def experiment_metadata(self):
        return dict(type=tuple_to_dict(models.Experiment.EXPERIMENT_TYPE_CHOICES))

    def animal_group_metadata(self):
        return dict(
            sex=models.AnimalGroup.SEX_DICT,
            generation=models.AnimalGroup.GENERATION_DICT,
            species=list(Species.objects.all().values("id", "name").order_by("id")),
            strains=list(Strain.objects.all().values("id", "species_id", "name").order_by("id")),
            lifestage=tuple_to_dict(models.AnimalGroup.LIFESTAGE_CHOICES),
        )

    def dosing_regime_metadata(self):
        return dict(
            route_of_exposure=models.DosingRegime.ROUTE_EXPOSURE_CHOICES_DICT,
            positive_control=tuple_to_dict(models.DosingRegime.POSITIVE_CONTROL_CHOICES),
            negative_control=tuple_to_dict(models.DosingRegime.NEGATIVE_CONTROL_CHOICES),
        )

    def dose_group_metadata(self):
        return dict(dose_units=list(DoseUnits.objects.all().values("id", "name").order_by("id")))

    def endpoint_metadata(self):
        return dict(
            litter_effects=tuple_to_dict(models.Endpoint.LITTER_EFFECT_CHOICES),
            observation_time_units=tuple_to_dict(models.Endpoint.OBSERVATION_TIME_UNITS),
            adversity_direction=tuple_to_dict(models.Endpoint.ADVERSE_DIRECTION_CHOICES),
            data_type=tuple_to_dict(models.Endpoint.DATA_TYPE_CHOICES),
            variance_type=tuple_to_dict(models.Endpoint.VARIANCE_TYPE_CHOICES),
            monotonicity=tuple_to_dict(models.Endpoint.MONOTONICITY_CHOICES),
            trend_result=tuple_to_dict(models.Endpoint.TREND_RESULT_CHOICES),
        )

    def evaluate(self):
        return dict(
            study=self.study_metadata(),
            experiment=self.experiment_metadata(),
            animal_group=self.animal_group_metadata(),
            dosing_regime=self.dosing_regime_metadata(),
            dose_group=self.dose_group_metadata(),
            endpoint=self.endpoint_metadata(),
        )
