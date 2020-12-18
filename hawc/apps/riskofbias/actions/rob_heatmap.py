import re
from typing import Any, Dict, Optional

import pandas as pd
import pydantic
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils.html import strip_tags

from hawc.apps.common.actions import BaseApiAction
from hawc.apps.riskofbias.models import RiskOfBiasScore
from hawc.apps.study.models import Study

from ...common.helper import FlatExport, empty_dataframe


class RobHeatmapData(pydantic.BaseModel):
    assessment_id: int
    unpublished: Optional[bool] = False
    bioassay: Optional[bool] = False
    epi: Optional[bool] = False
    invitro: Optional[bool] = False

    class Config:
        allow_mutation = False

    def __hash__(self) -> int:
        return hash(frozenset(self.dict().items()))


class RobHeatmapAction(BaseApiAction):
    """
    Copy final scores from a subset of studies from one assessment as the scores in a
    different assessment. Useful when an assessment is cloned or repurposed and existing
    evaluations are should be used in a new evaluation.
    """

    input_model = RobHeatmapData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputs: RobHeatmapData  # only done to set type inference

    def study_designs(self) -> pd.DataFrame:
        df = pd.DataFrame(
            Study.objects.filter(assessment_id=self.inputs.assessment_id).values(
                "id", "bioassay", "epi", "epi_meta", "in_vitro"
            )
        )
        df = (
            df.melt(id_vars="id", var_name="study types")
            .query("value==True")
            .drop(columns="value")
            .groupby("id")
            .agg({"study types": "|".join})
            .reset_index()
        )
        return df

    def create_heatmap(self) -> pd.DataFrame:
        qs_term_mapping = dict(
            riskofbias__study__id="study id",
            riskofbias__study__short_citation="study short citation",
            metric__domain__id="evaluation domain id",
            metric__domain__name="evaluation domain name",
            metric_id="evaluation metric id",
            metric__name="evaluation metric name",
            metric__short_name="evaluation metric short name",
            id="evaluation id",
            label="evaluation label",
            score="evaluation value",
            bias_direction="evaluation bias direction",
            notes="evaluation notes",
        )
        scores = RiskOfBiasScore.objects.filter(
            riskofbias__final=True,
            riskofbias__active=True,
            riskofbias__study__assessment_id=self.inputs.assessment_id,
        ).select_related("riskofbias", "riskofbias__study", "metric", "metric__domain")

        # optionally filter to show unpublished data
        if not self.inputs.unpublished:
            scores = scores.filter(riskofbias__study__published=True)

        # optionally filter by study design
        q_metric_types = Q()
        if self.inputs.bioassay:
            q_metric_types |= Q(metric__required_animal=True)
        if self.inputs.epi:
            q_metric_types |= Q(metric__required_epi=True)
        if self.inputs.invitro:
            q_metric_types |= Q(metric__required_invitro=True)

        if len(q_metric_types) == 0:
            scores = scores.none()
        else:
            scores = scores.filter(q_metric_types)

        if scores.count() == 0:
            return empty_dataframe()

        qs = scores.values(*list(qs_term_mapping.keys()))
        df = pd.DataFrame(list(qs))

        df.loc[:, "evaluation symbol"] = df.score.map(RiskOfBiasScore.SCORE_SYMBOLS)
        df.loc[:, "evaluation text"] = df.score.map(RiskOfBiasScore.RISK_OF_BIAS_SCORE_CHOICES_MAP)
        df.loc[:, "evaluation direction text"] = df.bias_direction.map(
            RiskOfBiasScore.BIAS_DIRECTION_CHOICES_MAP
        )
        df.loc[:, "evaluation"] = df["evaluation symbol"] + " " + df["evaluation text"]
        df.loc[:, "notes"] = df.notes.apply(strip_tags)
        df.loc[:, "label"] = df.label.str.replace(re.compile(r"$^"), "Overall")
        df = df.rename(columns=qs_term_mapping)
        df = df.merge(
            self.study_designs(), left_on="study id", right_on="id", how="left"
        ).sort_values(by=["study id", "id"])
        return df

    def evaluate(self) -> Dict[str, Any]:
        key = f"assessment-{self.inputs.assessment_id}-rob-heatmap-{hash(self.inputs)}"
        df = cache.get(key)
        if df is None:
            df = self.create_heatmap()
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df, filename=key)
        return export
