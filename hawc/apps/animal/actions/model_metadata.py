from pydantic import BaseModel

from hawc.apps.animal import constants, models
from hawc.apps.assessment.models import DoseUnits, Species, Strain
from hawc.apps.common.actions import BaseApiAction
from hawc.apps.study.models import Study


def tuple_to_dict(tuple):
    return {e[0]: e[1] for e in tuple}


def enum_to_dict(Enum):
    return {e.value: e.label for e in Enum}


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
        return dict(type=enum_to_dict(constants.ExperimentType))

    def animal_group_metadata(self):
        return dict(
            sex=enum_to_dict(constants.Sex),
            generation=enum_to_dict(constants.Generation),
            species=list(Species.objects.all().values("id", "name").order_by("id")),
            strains=list(Strain.objects.all().values("id", "species_id", "name").order_by("id")),
            lifestage=enum_to_dict(constants.Lifestage),
        )

    def dosing_regime_metadata(self):
        return dict(
            route_of_exposure=enum_to_dict(constants.RouteExposure),
            positive_control=tuple_to_dict(models.DosingRegime.POSITIVE_CONTROL_CHOICES),
            negative_control=enum_to_dict(constants.NegativeControl),
        )

    def dose_group_metadata(self):
        return dict(dose_units=list(DoseUnits.objects.all().values("id", "name").order_by("id")))

    def endpoint_metadata(self):
        return dict(
            litter_effects=enum_to_dict(constants.LitterEffect),
            observation_time_units=enum_to_dict(constants.ObservationTimeUnits),
            adversity_direction=enum_to_dict(constants.AdverseDirection),
            data_type=enum_to_dict(constants.DataType),
            variance_type=enum_to_dict(constants.VarianceType),
            monotonicity=enum_to_dict(constants.Monotonicity),
            trend_result=enum_to_dict(constants.TrendResult),
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
