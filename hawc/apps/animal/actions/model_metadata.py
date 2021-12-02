from pydantic import BaseModel

from hawc.apps.animal import constants, models
from hawc.apps.assessment.models import DoseUnits, Species, Strain
from hawc.apps.common.actions import BaseApiAction
from hawc.apps.common.helper import choices_to_dict
from hawc.apps.study.models import Study


class NoInput(BaseModel):
    pass


class AnimalMetadata(BaseApiAction):
    """
    Generate a dictionary of field choices for all animal models.
    """

    input_model = NoInput

    def study_metadata(self):
        return dict(coi_reported=dict(Study.COI_REPORTED_CHOICES))

    def experiment_metadata(self):
        return dict(type=choices_to_dict(constants.ExperimentType))

    def animal_group_metadata(self):
        return dict(
            sex=choices_to_dict(constants.Sex),
            generation=choices_to_dict(constants.Generation),
            species=list(Species.objects.all().values("id", "name").order_by("id")),
            strains=list(Strain.objects.all().values("id", "species_id", "name").order_by("id")),
            lifestage=choices_to_dict(constants.Lifestage),
        )

    def dosing_regime_metadata(self):
        return dict(
            route_of_exposure=choices_to_dict(constants.RouteExposure),
            positive_control=dict(models.DosingRegime.POSITIVE_CONTROL_CHOICES),
            negative_control=choices_to_dict(constants.NegativeControl),
        )

    def dose_group_metadata(self):
        return dict(dose_units=list(DoseUnits.objects.all().values("id", "name").order_by("id")))

    def endpoint_metadata(self):
        return dict(
            litter_effects=choices_to_dict(constants.LitterEffect),
            observation_time_units=choices_to_dict(constants.ObservationTimeUnits),
            adversity_direction=choices_to_dict(constants.AdverseDirection),
            data_type=choices_to_dict(constants.DataType),
            variance_type=choices_to_dict(constants.VarianceType),
            monotonicity=choices_to_dict(constants.Monotonicity),
            trend_result=choices_to_dict(constants.TrendResult),
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
