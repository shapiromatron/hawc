from typing import List, Optional

import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models


class FinalRiskOfBiasScoreQuerySet(models.QuerySet):
    def endpoint_scores(self, endpoint_ids: List[int]):

        Endpoint = apps.get_model("animal", "Endpoint")
        AnimalGroup = apps.get_model("animal", "AnimalGroup")

        endpoints = Endpoint.objects.filter(pk__in=endpoint_ids).select_related(
            "animal_group__experiment"
        )

        score_values = self.values()
        endpoint_scores = {endpoint_id: {} for endpoint_id in endpoint_ids}

        def default_scores(endpoint, score_values):
            return [
                (score["metric_id"], score)
                for score in score_values
                if endpoint.animal_group.experiment.study_id == score["study_id"]
                and score["is_default"]
            ]

        def animal_group_overrides(endpoint, score_values):
            content_type_id = ContentType.objects.get_for_model(AnimalGroup).id
            return [
                (score["metric_id"], score)
                for score in score_values
                if endpoint.animal_group.experiment.study_id == score["study_id"]
                and score["content_type_id"] == content_type_id
                and endpoint.animal_group_id == score["object_id"]
            ]

        def endpoint_overrides(endpoint, score_values):
            content_type_id = ContentType.objects.get_for_model(Endpoint).id
            return [
                (score["metric_id"], score)
                for score in score_values
                if endpoint.animal_group.experiment.study_id == score["study_id"]
                and score["content_type_id"] == content_type_id
                and endpoint.id == score["object_id"]
            ]

        for endpoint in endpoints:
            for metric_id, score in default_scores(endpoint, score_values):
                endpoint_scores[endpoint.id][metric_id] = score
            for metric_id, score in animal_group_overrides(endpoint, score_values):
                endpoint_scores[endpoint.id][metric_id] = score
            for metric_id, score in endpoint_overrides(endpoint, score_values):
                endpoint_scores[endpoint.id][metric_id] = score

        return endpoint_scores


class FinalRiskOfBiasScoreManager(models.Manager):
    def get_queryset(self):
        return FinalRiskOfBiasScoreQuerySet(self.model, using=self._db)

    def overall_endpoint_scores(self, assessment_id: int) -> Optional[pd.DataFrame]:
        qs = self.filter(
            study__assessment_id=assessment_id, metric__domain__is_overall_confidence=True
        )
        if qs.count() == 0:
            return None

        endpoint_ids = qs.values_list("study__experiments__animal_groups__endpoints", flat=True)
        endpoint_scores = qs.endpoint_scores(endpoint_ids)

        RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
        SCORE_CHOICES_MAP = RiskOfBiasScore.RISK_OF_BIAS_SCORE_CHOICES_MAP
        SCORE_SYMBOLS = RiskOfBiasScore.SCORE_SYMBOLS

        rows = []
        for endpoint_id, scores in endpoint_scores.items():
            for score in scores.values():
                overall_evaluation = f"{SCORE_CHOICES_MAP[score['score_score']]} ({SCORE_SYMBOLS[score['score_score']]})"
                rows.append((endpoint_id, overall_evaluation))

        return pd.DataFrame(data=rows, columns=("endpoint id", "overall study evaluation"))
