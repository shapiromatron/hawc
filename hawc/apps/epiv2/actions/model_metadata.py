from django.db.models.functions import Lower
from rest_framework.response import Response

from hawc.apps.common.actions import BaseApiAction
from hawc.apps.epi.actions.model_metadata import NoInput, get_all_model_objects
from hawc.apps.epiv2 import constants, models

from ...epi.models import Country


class EpiV2AssessmentMetadata(BaseApiAction):
    """
    Generate an assessment-specific dictionary of field choices for all epiv2 models.
    """

    assessment = None

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
        metadata = dict(
            variance_type=dict(constants.VarianceType.choices),
            ci_type=dict(constants.ConfidenceIntervalType.choices),
        )
        metadata["assessment_specific_chemicals"] = {
            chem.id: chem.name
            for chem in models.Chemical.objects.filter(
                design__study__assessment=self.assessment
            ).order_by(Lower("name"))
        }
        return metadata

    def outcome_metadata(self):
        metadata = dict(
            system=dict(constants.HealthOutcomeSystem.choices),
        )
        return metadata

    def data_extraction_metadata(self):
        metadata = dict(
            ci_type=dict(constants.ConfidenceIntervalType.choices),
            variance_type=dict(constants.VarianceType.choices),
            significant=dict(constants.Significant.choices),
        )

        metadata["assessment_specific_adjustment_factors"] = {
            af.id: {"name": af.name, "description": af.description}
            for af in models.AdjustmentFactor.objects.filter(
                design__study__assessment=self.assessment
            ).order_by(Lower("name"))
        }
        return metadata

    def evaluate(self):
        return dict(
            design=self.design_metadata(),
            exposure_metadata=self.exposure_metadata(),
            exposure_level_metadata=self.exposure_level_metadata(),
            outcome_metadata=self.outcome_metadata(),
            data_extraction_metadata=self.data_extraction_metadata(),
        )

    def handle_assessment_request(self, request, assessment):
        self.assessment = assessment
        return Response(self.evaluate())
