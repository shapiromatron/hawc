from typing import Optional

import pandas as pd
from django.db import models
from django.db.models import Case, Count, IntegerField, Sum, Value, When

from ..common.models import BaseManager


class RiskOfBiasDomainManager(BaseManager):
    assessment_relation = "assessment"


class RiskOfBiasMetricManager(BaseManager):
    assessment_relation = "domain__assessment"

    def get_required_metrics(self, assessment, study):
        requireds = models.Q()
        if study.bioassay:
            requireds |= models.Q(required_animal=True)
        if study.epi or study.epi_meta:
            requireds |= models.Q(required_epi=True)
        if study.in_vitro:
            requireds |= models.Q(required_invitro=True)
        return self.get_qs(assessment).filter(requireds)

    def get_metrics_for_visuals(self, assessment_id):
        return self.get_qs(assessment_id).values("id", "name")


class RiskOfBiasQuerySet(models.QuerySet):
    def num_scores(self):
        return self.annotate(num_scores=Count("scores"))

    def num_override_scores(self):
        return self.annotate(
            num_override_scores=Sum(
                Case(
                    When(scores__is_default=False, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
        )


class RiskOfBiasManager(BaseManager):

    assessment_relation = "study__assessment"

    def get_queryset(self):
        return RiskOfBiasQuerySet(self.model, using=self._db)

    def all_active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True)

    def active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True, final=False)


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = "riskofbias__study__assessment"

    def overall_scores(self, assessment_id: int) -> Optional[pd.DataFrame]:
        qs = self.filter(
            riskofbias__active=True,
            riskofbias__final=True,
            riskofbias__study__assessment_id=assessment_id,
            metric__domain__is_overall_confidence=True,
            is_default=True,
        ).values_list("riskofbias__study_id", "score")

        if qs.count() == 0:
            return None

        SCORE_CHOICES_MAP = self.model.RISK_OF_BIAS_SCORE_CHOICES_MAP
        SCORE_SYMBOLS = self.model.SCORE_SYMBOLS
        rows = []
        for (id, score) in qs:
            overall_evaluation = f"{SCORE_CHOICES_MAP[score]} ({SCORE_SYMBOLS[score]})"
            rows.append((id, overall_evaluation))

        return pd.DataFrame(
            data=rows, columns=("study id", "overall study evaluation")
        ).drop_duplicates(subset=["study id"])


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = "assessment"
