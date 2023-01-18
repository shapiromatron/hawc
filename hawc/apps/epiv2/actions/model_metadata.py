from ...common.actions import BaseApiAction
from ...epi.actions.model_metadata import NoInput, get_all_model_objects
from ...epi.models import Country
from ...study.models import Study
from .. import constants


class EpiV2Metadata(BaseApiAction):
    """
    Generate a dictionary of field choices for all epiv2 models.
    """

    input_model = NoInput

    def design_metadata(self):
        return dict(
            study_design=dict(constants.StudyDesign.choices),
            source=dict(constants.Source.choices),
            age_profile=dict(constants.AgeProfile.choices),
            sex=dict(constants.Sex.choices),
            countries=get_all_model_objects(Country, "name", "code"),
        )

    def exposure_metadata(self):
        metadata = dict(
            measurement_type=dict(constants.MeasurementType.choices),
            biomonitoring_matrix=dict(constants.BiomonitoringMatrix.choices),
            biomonitoring_source=dict(constants.BiomonitoringSource.choices),
            exposure_route=dict(constants.ExposureRoute.choices),
        )
        return metadata

    def exposure_level_metadata(self):
        return dict(
            variance_type=dict(constants.VarianceType.choices),
            ci_type=dict(constants.ConfidenceIntervalType.choices),
        )

    def outcome_metadata(self):
        metadata = dict(
            system=dict(constants.HealthOutcomeSystem.choices),
        )
        return metadata

    def data_extraction_metadata(self):
        return dict(
            effect_estimate_type=dict(constants.EffectEstimateType.choices),
            ci_type=dict(constants.ConfidenceIntervalType.choices),
            variance_type=dict(constants.VarianceType.choices),
            significant=dict(constants.Significant.choices),
            transforms=dict(constants.DataTransforms.choices),
        )

    def evaluate(self) -> dict:
        return dict(
            study=Study.metadata(),
            design=self.design_metadata(),
            exposure=self.exposure_metadata(),
            exposure_level=self.exposure_level_metadata(),
            outcome=self.outcome_metadata(),
            data_extraction=self.data_extraction_metadata(),
        )
