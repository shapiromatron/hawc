from typing import List, Optional

import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models


class FinalRiskOfBiasScoreQuerySet(models.QuerySet):
    def _default_tuples(self, score_values, study_id):
        return [
            (score["metric_id"], score)
            for score in score_values
            if study_id == score["study_id"] and score["is_default"]
        ]

    def _override_tuples(self, score_values, study_id, override_model, object_id):
        content_type_id = ContentType.objects.get_for_model(override_model).id
        return [
            (score["metric_id"], score)
            for score in score_values
            if study_id == score["study_id"]
            and score["content_type_id"] == content_type_id
            and object_id == score["object_id"]
        ]

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

    def result_scores(self, result_ids: List[int]):

        Result = apps.get_model("epi", "Result")
        Outcome = apps.get_model("epi", "Outcome")

        results = Result.objects.filter(pk__in=result_ids).select_related(
            "outcome__study_population"
        )

        score_values = self.values()
        result_scores = {result_id: {} for result_id in result_ids}

        for result in results:
            study_id = result.outcome.study_population.study_id
            for metric_id, score in self._default_tuples(score_values, study_id):
                result_scores[result.id][metric_id] = score
            for metric_id, score in self._override_tuples(
                score_values, study_id, Outcome, result.outcome_id
            ):
                result_scores[result.id][metric_id] = score
            for metric_id, score in self._override_tuples(
                score_values, study_id, Result, result.id
            ):
                result_scores[result.id][metric_id] = score

        return result_scores


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

    def overall_result_scores(self, assessment_id: int) -> Optional[pd.DataFrame]:
        qs = self.filter(
            study__assessment_id=assessment_id, metric__domain__is_overall_confidence=True
        )
        if qs.count() == 0:
            return None

        result_ids = qs.values_list("study__study_populations__outcomes__results", flat=True)
        result_scores = qs.result_scores(result_ids)

        RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
        SCORE_CHOICES_MAP = RiskOfBiasScore.RISK_OF_BIAS_SCORE_CHOICES_MAP
        SCORE_SYMBOLS = RiskOfBiasScore.SCORE_SYMBOLS

        rows = []
        for result_id, scores in result_scores.items():
            for score in scores.values():
                overall_evaluation = f"{SCORE_CHOICES_MAP[score['score_score']]} ({SCORE_SYMBOLS[score['score_score']]})"
                rows.append((result_id, overall_evaluation))

        return pd.DataFrame(data=rows, columns=("result id", "overall study evaluation"))
