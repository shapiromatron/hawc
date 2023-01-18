from pydantic import BaseModel

from ...assessment.models import DoseUnits, Species, Strain
from ...common.actions import BaseApiAction
from ...study.models import Study
from .. import constants


class NoInput(BaseModel):
    pass


class AnimalMetadata(BaseApiAction):
    """
    Generate a dictionary of field choices for all animal models.
    """

    input_model = NoInput

    def experiment_metadata(self):
        return dict(type=dict(constants.ExperimentType.choices))

    def animal_group_metadata(self):
        return dict(
            sex=dict(constants.Sex.choices),
            generation=dict(constants.Generation.choices),
            species=list(Species.objects.all().values("id", "name").order_by("id")),
            strains=list(Strain.objects.all().values("id", "species_id", "name").order_by("id")),
            lifestage=dict(constants.Lifestage.choices),
        )

    def dosing_regime_metadata(self):
        return dict(
            route_of_exposure=dict(constants.RouteExposure.choices),
            positive_control=dict(constants.POSITIVE_CONTROL_CHOICES),
            negative_control=dict(constants.NegativeControl.choices),
        )

    def dose_group_metadata(self):
        return dict(dose_units=list(DoseUnits.objects.all().values("id", "name").order_by("id")))

    def endpoint_metadata(self):
        return dict(
            litter_effects=dict(constants.LitterEffect.choices),
            observation_time_units=dict(constants.ObservationTimeUnits.choices),
            adversity_direction=dict(constants.AdverseDirection.choices),
            data_type=dict(constants.DataType.choices),
            variance_type=dict(constants.VarianceType.choices),
            monotonicity=dict(constants.Monotonicity.choices),
            trend_result=dict(constants.TrendResult.choices),
        )

    def evaluate(self) -> dict:
        return dict(
            study=Study.metadata(),
            experiment=self.experiment_metadata(),
            animal_group=self.animal_group_metadata(),
            dosing_regime=self.dosing_regime_metadata(),
            dose_group=self.dose_group_metadata(),
            endpoint=self.endpoint_metadata(),
        )
