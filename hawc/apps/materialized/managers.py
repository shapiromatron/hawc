from itertools import chain
from typing import NamedTuple

import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ..riskofbias.constants import SCORE_CHOICES_MAP, SCORE_SYMBOLS


class MetricScore(NamedTuple):
    metric_id: int
    score: dict


class FinalRiskOfBiasScoreQuerySet(models.QuerySet):
    @property
    def score_values(self):
        if not hasattr(self, "_score_values"):
            self._score_values = self.values()
        return self._score_values

    def _study_scores(self, study_id: int) -> list[dict]:
        return [score for score in self.score_values if study_id == score["study_id"]]

    def _default_tuples(self, scores: list[dict]) -> list[MetricScore]:
        return [MetricScore(score["metric_id"], score) for score in scores if score["is_default"]]

    def _override_tuples(
        self, scores: list[dict], override_model, object_id: int
    ) -> list[MetricScore]:
        content_type_id = ContentType.objects.get_for_model(override_model).id
        return [
            MetricScore(score["metric_id"], score)
            for score in scores
            if score["content_type_id"] == content_type_id and object_id == score["object_id"]
        ]

    def study_scores(self, study_ids: list[int]) -> dict[tuple[int, int], dict]:
        """Return default scores for study and metric.

        Args:
            study_ids (list[int]): A list of study ids

        Returns:
            dict[tuple[int, int], dict]: Keys are equal to (study_id, metric_id)
        """
        return {
            (score["study_id"], score["metric_id"]): score
            for score in self.score_values
            if score["study_id"] in study_ids and score["is_default"]
        }

    def endpoint_scores(self, endpoint_ids: list[int]) -> dict[tuple[int, int], dict]:
        Endpoint = apps.get_model("animal", "Endpoint")
        AnimalGroup = apps.get_model("animal", "AnimalGroup")

        endpoints = Endpoint.objects.filter(pk__in=endpoint_ids).select_related(
            "animal_group__experiment"
        )

        endpoint_scores = {}

        for endpoint in endpoints:
            study_id = endpoint.animal_group.experiment.study_id
            study_scores = self._study_scores(study_id)
            for metric_id, score in chain(
                self._default_tuples(study_scores),
                self._override_tuples(study_scores, AnimalGroup, endpoint.animal_group_id),
                self._override_tuples(study_scores, Endpoint, endpoint.id),
            ):
                endpoint_scores[endpoint.id, metric_id] = score

        return endpoint_scores

    def outcome_scores(self, outcome_ids: list[int]) -> dict[tuple[int, int], dict]:
        Outcome = apps.get_model("epi", "Outcome")

        outcomes = Outcome.objects.filter(pk__in=outcome_ids).select_related("study_population")

        outcome_scores = {}

        for outcome in outcomes:
            study_id = outcome.study_population.study_id
            study_scores = self._study_scores(study_id)
            for metric_id, score in chain(
                self._default_tuples(study_scores),
                self._override_tuples(study_scores, Outcome, outcome.id),
            ):
                outcome_scores[outcome.id, metric_id] = score

        return outcome_scores

    def result_scores(self, result_ids: list[int]) -> dict[tuple[int, int], dict]:
        Result = apps.get_model("epi", "Result")
        Outcome = apps.get_model("epi", "Outcome")
        Exposure = apps.get_model("epi", "Exposure")

        results = Result.objects.filter(pk__in=result_ids).select_related(
            "outcome__study_population", "comparison_set"
        )

        result_scores = {}

        for result in results:
            study_id = result.outcome.study_population.study_id
            study_scores = self._study_scores(study_id)
            for metric_id, score in chain(
                self._default_tuples(study_scores),
                self._override_tuples(study_scores, Exposure, result.comparison_set.exposure_id),
                self._override_tuples(study_scores, Outcome, result.outcome_id),
                self._override_tuples(study_scores, Result, result.id),
            ):
                result_scores[result.id, metric_id] = score

        return result_scores


class FinalRiskOfBiasScoreManager(models.Manager):
    def get_queryset(self):
        return FinalRiskOfBiasScoreQuerySet(self.model, using=self._db)

    def overall_endpoint_scores(self, assessment_id: int) -> pd.DataFrame | None:
        qs = self.filter(
            study__assessment_id=assessment_id, metric__domain__is_overall_confidence=True
        )
        if qs.count() == 0:
            return None

        endpoint_ids = qs.values_list("study__experiments__animal_groups__endpoints", flat=True)
        endpoint_scores = qs.endpoint_scores(endpoint_ids)

        rows = []
        for (endpoint_id, _), score in endpoint_scores.items():
            overall_evaluation = (
                f"{SCORE_CHOICES_MAP[score['score_score']]} ({SCORE_SYMBOLS[score['score_score']]})"
            )
            rows.append((endpoint_id, overall_evaluation))

        return pd.DataFrame(data=rows, columns=("endpoint id", "overall study evaluation"))

    def overall_result_scores(self, assessment_id: int) -> pd.DataFrame | None:
        qs = self.filter(
            study__assessment_id=assessment_id, metric__domain__is_overall_confidence=True
        )
        if qs.count() == 0:
            return None

        result_ids = qs.values_list("study__study_populations__outcomes__results", flat=True)
        result_scores = qs.result_scores(result_ids)

        rows = []
        for (result_id, _), score in result_scores.items():
            overall_evaluation = (
                f"{SCORE_CHOICES_MAP[score['score_score']]} ({SCORE_SYMBOLS[score['score_score']]})"
            )
            rows.append((result_id, overall_evaluation))

        return pd.DataFrame(data=rows, columns=("result id", "overall study evaluation"))
