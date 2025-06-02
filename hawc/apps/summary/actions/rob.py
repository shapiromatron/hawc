from ...common.models import sql_display
from ...riskofbias import models
from ...riskofbias.constants import (
    SCORE_CHOICES_MAP,
    SCORE_SHADES,
    SCORE_SYMBOLS,
    BiasDirections,
)
from ..constants import StudyType


def get_rob_visual_form_data(assessment_id: int, study_type: StudyType):
    metrics = (
        models.RiskOfBiasMetric.objects.filter(
            **{
                f"{study_type.rob_prefix()}": True,
                "domain__assessment_id": assessment_id,
            }
        )
        .values(
            "id",
            "name",
            "sort_order",
            "domain__id",
            "domain__name",
            "domain__sort_order",
        )
        .order_by(
            "domain__sort_order",
            "sort_order",
        )
    )
    scores = (
        models.RiskOfBiasScore.objects.filter(
            **{
                "riskofbias__final": True,
                "riskofbias__study__assessment_id": assessment_id,
                f"riskofbias__study__{study_type.study_filter_prefix()}": True,
            }
        )
        .annotate(
            score_label=sql_display("score", SCORE_CHOICES_MAP),
            score_symbol=sql_display("score", SCORE_SYMBOLS),
            score_shade=sql_display("score", SCORE_SHADES),
            bias_direction_label=sql_display("score", BiasDirections),
        )
        .values(
            "id",
            "score",
            "score_label",
            "score_symbol",
            "score_shade",
            "bias_direction",
            "bias_direction_label",
            "label",
            "is_default",
            "riskofbias__study__id",
            "riskofbias__study__short_citation",
            "riskofbias__study__study_identifier",
            "riskofbias__study__published",
            "metric_id",
            "metric__name",
            "metric__sort_order",
            "metric__domain_id",
            "metric__domain__name",
            "metric__domain__sort_order",
        )
        .order_by(
            "riskofbias__study__short_citation",
            "metric__domain__sort_order",
            "metric__sort_order",
        )
    )
    return {
        "metrics": metrics,
        "scores": scores,
    }
