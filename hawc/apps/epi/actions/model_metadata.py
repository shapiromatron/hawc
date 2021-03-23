from django.db.models.functions import Lower
from pydantic import BaseModel
from rest_framework.response import Response

from hawc.apps.assessment.models import DoseUnits
from hawc.apps.common.actions import BaseApiAction
from hawc.apps.epi.models import (
    AdjustmentFactor,
    CentralTendency,
    Country,
    Criteria,
    Ethnicity,
    Group,
    GroupNumericalDescriptions,
    GroupResult,
    Outcome,
    Result,
    ResultMetric,
    StudyPopulation,
)


def tuple_to_dict(tuple):
    return {e[0]: e[1] for e in tuple}


def get_all_model_objects(object_class, display_field="name", val_field="id"):
    object_values = object_class.objects.all().order_by(Lower(display_field)).values()
    return {x[val_field]: x[display_field] for x in object_values}


class NoInput(BaseModel):
    pass


class EpiMetadata(BaseApiAction):
    """
    Generate a dictionary of field choices for all epi models.
    """

    input_model = NoInput

    def central_tendency_metadata(self):
        return dict(
            estimate_type=dict(CentralTendency.ESTIMATE_TYPE_CHOICES),
            variance_type=dict(CentralTendency.VARIANCE_TYPE_CHOICES),
        )

    def exposure_metadata(self):
        return {"dose_units": get_all_model_objects(DoseUnits)}

    def group_numerical_descriptions_metadata(self):
        return dict(
            mean_type=dict(GroupNumericalDescriptions.MEAN_TYPE_CHOICES),
            variance_type=dict(GroupNumericalDescriptions.VARIANCE_TYPE_CHOICES),
            lower_type=dict(GroupNumericalDescriptions.LOWER_LIMIT_CHOICES),
            upper_type=dict(GroupNumericalDescriptions.UPPER_LIMIT_CHOICES),
        )

    def group_metadata(self):
        return dict(sex=dict(Group.SEX_CHOICES), ethnicities=get_all_model_objects(Ethnicity))

    def group_result_metadata(self):
        return dict(
            p_value_qualifier=dict(GroupResult.P_VALUE_QUALIFIER_CHOICES),
            main_finding=dict(GroupResult.MAIN_FINDING_CHOICES),
        )

    def result_metadata(self):
        return dict(
            dose_response=dict(Result.DOSE_RESPONSE_CHOICES),
            statistical_power=dict(Result.STATISTICAL_POWER_CHOICES),
            estimate_type=dict(Result.ESTIMATE_TYPE_CHOICES),
            variance_type=dict(Result.VARIANCE_TYPE_CHOICES),
            metrics=get_all_model_objects(ResultMetric, "metric"),
        )

    def outcome_metadata(self):
        return dict(diagnostic=dict(Outcome.DIAGNOSTIC_CHOICES),)

    def study_population_metadata(self):
        return dict(
            design=dict(StudyPopulation.DESIGN_CHOICES),
            countries=get_all_model_objects(Country, "name", "code"),
        )

    def evaluate(self):
        return dict(
            study_population=self.study_population_metadata(),
            outcome=self.outcome_metadata(),
            result=self.result_metadata(),
            group_result=self.group_result_metadata(),
            group=self.group_metadata(),
            group_numerical_descriptions=self.group_numerical_descriptions_metadata(),
            exposure=self.exposure_metadata(),
            central_tendency=self.central_tendency_metadata(),
        )


class EpiAssessmentMetadata(EpiMetadata):
    assessment = None

    def handle_assessment_request(self, request, assessment):
        self.assessment = assessment
        return Response(self.evaluate())

    def study_population_metadata(self):
        data = super().study_population_metadata()
        data["assessment_specific_criteria"] = {
            c.id: c.description
            for c in Criteria.objects.filter(assessment=self.assessment).order_by(
                Lower("description")
            )
        }
        return data

    def result_metadata(self):
        data = super().result_metadata()
        data["assessment_specific_adjustment_factors"] = {
            af.id: af.description
            for af in AdjustmentFactor.objects.filter(assessment=self.assessment).order_by(
                Lower("description")
            )
        }
        return data
