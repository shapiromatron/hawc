from django.db.models.functions import Lower
from pydantic import BaseModel

from ...assessment.models import DoseUnits
from ...common.actions import BaseApiAction
from ...study.models import Study
from .. import constants
from ..models import AdjustmentFactor, Country, Criteria, Ethnicity, ResultMetric


def get_all_model_objects(object_class, display_field="name", val_field="id"):
    object_values = object_class.objects.all().order_by(Lower(display_field)).values()
    return {x[val_field]: x[display_field] for x in object_values}


class NoInput(BaseModel):
    pass


class EpiAssessmentMetadata(BaseApiAction):
    """
    Generate an assessment-specific dictionary of field choices for all epi models.
    """

    assessment = None

    input_model = NoInput

    def central_tendency_metadata(self):
        return dict(
            estimate_type=dict(constants.EstimateType.choices),
            variance_type=dict(constants.VarianceType.choices),
        )

    def exposure_metadata(self):
        return {"dose_units": get_all_model_objects(DoseUnits)}

    def group_numerical_descriptions_metadata(self):
        return dict(
            mean_type=dict(constants.GroupMeanType.choices),
            variance_type=dict(constants.GroupVarianceType.choices),
            lower_type=dict(constants.LowerLimit.choices),
            upper_type=dict(constants.UpperLimit.choices),
        )

    def group_metadata(self):
        return dict(sex=dict(constants.Sex.choices), ethnicities=get_all_model_objects(Ethnicity))

    def group_result_metadata(self):
        return dict(
            p_value_qualifier=dict(constants.PValueQualifier.choices),
            main_finding=dict(constants.MainFinding.choices),
        )

    def result_metadata(self):
        metadata = dict(
            dose_response=dict(constants.DoseResponse.choices),
            statistical_power=dict(constants.StatisticalPower.choices),
            estimate_type=dict(constants.EstimateType.choices),
            variance_type=dict(constants.VarianceType.choices),
            metrics=get_all_model_objects(ResultMetric, "metric"),
        )

        metadata["assessment_specific_adjustment_factors"] = {
            af.id: af.description
            for af in AdjustmentFactor.objects.filter(assessment=self.data["assessment"]).order_by(
                Lower("description")
            )
        }

        return metadata

    def outcome_metadata(self):
        return dict(
            diagnostic=dict(constants.Diagnostic.choices),
        )

    def study_population_metadata(self):
        metadata = dict(
            design=dict(constants.Design.choices),
            countries=get_all_model_objects(Country, "name", "code"),
        )
        metadata["assessment_specific_criteria"] = {
            c.id: c.description
            for c in Criteria.objects.filter(assessment=self.data["assessment"]).order_by(
                Lower("description")
            )
        }

        return metadata

    def evaluate(self) -> dict:
        return dict(
            study=Study.metadata(),
            study_population=self.study_population_metadata(),
            outcome=self.outcome_metadata(),
            result=self.result_metadata(),
            group_result=self.group_result_metadata(),
            group=self.group_metadata(),
            group_numerical_descriptions=self.group_numerical_descriptions_metadata(),
            exposure=self.exposure_metadata(),
            central_tendency=self.central_tendency_metadata(),
        )
