import pytest
from django.contrib.contenttypes.models import ContentType

from hawc.apps.animal.models import Endpoint
from hawc.apps.materialized import models
from hawc.apps.riskofbias.models import RiskOfBiasScore, RiskOfBiasScoreOverrideObject


@pytest.mark.django_db
class TestFinalRiskOfBiasScoreManager:
    def test_study_scores(self):
        study_ids = [1, 3, 4]
        actual_scores = models.FinalRiskOfBiasScore.objects.all().study_scores(study_ids)
        expected_scores = RiskOfBiasScore.objects.filter(
            is_default=True,
            riskofbias__final=True,
            riskofbias__active=True,
            riskofbias__study_id__in=study_ids,
        ).select_related("riskofbias")
        # actual scores and expected scores should be the same
        assert len(actual_scores) == len(expected_scores)
        for (study_id, metric_id), actual_value in actual_scores.items():
            assert actual_value["score_id"] == next(
                score.id
                for score in expected_scores
                if score.riskofbias.study_id == study_id and score.metric_id == metric_id
            )

    def test_endpoint_scores(self):
        # endpoint 1 has an endpoint level override
        endpoint_id = 1
        actual_scores = models.FinalRiskOfBiasScore.objects.all().endpoint_scores([endpoint_id])
        endpoint = Endpoint.objects.get(pk=endpoint_id)
        content_type = ContentType.objects.get_for_model(endpoint)
        override = (
            RiskOfBiasScoreOverrideObject.objects.filter(
                content_type=content_type, object_id=endpoint.id
            )
            .select_related("score__riskofbias")
            .first()
        )
        expected_score = override.score
        assert expected_score.riskofbias.final and expected_score.riskofbias.active
        assert (
            actual_scores[(endpoint_id, expected_score.metric_id)]["score_id"] == expected_score.id
        )

        # endpoint 3 has an animal group level override
        endpoint_id = 3
        actual_scores = models.FinalRiskOfBiasScore.objects.all().endpoint_scores([endpoint_id])
        animal_group = Endpoint.objects.get(pk=endpoint_id).animal_group
        content_type = ContentType.objects.get_for_model(animal_group)
        override = RiskOfBiasScoreOverrideObject.objects.filter(
            content_type=content_type, object_id=animal_group.id
        ).first()
        expected_score = override.score
        assert expected_score.riskofbias.final and expected_score.riskofbias.active
        assert (
            actual_scores[(endpoint_id, expected_score.metric_id)]["score_id"] == expected_score.id
        )

        # endpoint 2 has no override
        endpoint_id = 2
        endpoint = Endpoint.objects.get(pk=endpoint_id)
        endpoint_study_id = endpoint.animal_group.experiment.study_id
        actual_scores = models.FinalRiskOfBiasScore.objects.all().endpoint_scores([endpoint_id])
        expected_scores = RiskOfBiasScore.objects.filter(
            is_default=True,
            riskofbias__final=True,
            riskofbias__active=True,
            riskofbias__study_id=endpoint_study_id,
        ).select_related("riskofbias")
        assert len(actual_scores) == len(expected_scores)
        for (endpoint_id, metric_id), actual_value in actual_scores.items():
            assert actual_value["score_id"] == next(
                score.id
                for score in expected_scores
                if score.riskofbias.study_id == endpoint_study_id and score.metric_id == metric_id
            )
