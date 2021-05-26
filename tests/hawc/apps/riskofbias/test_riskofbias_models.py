import json
from textwrap import dedent

import pytest
from django.urls import reverse

from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore, RiskOfBiasScoreOverrideObject


@pytest.mark.django_db
class TestRiskOfBiasScoreOverrideObject:
    def test_get_object_url(self):
        valid = RiskOfBiasScoreOverrideObject.objects.get(id=2)
        assert valid.get_object_url() == valid.content_object.get_absolute_url()

        invalid = RiskOfBiasScoreOverrideObject.objects.get(id=3)
        assert invalid.get_object_url() == reverse("404")

    def test_get_object_name(self):
        valid = RiskOfBiasScoreOverrideObject.objects.get(id=2)
        assert valid.get_object_name() == "sd rats"

        invalid = RiskOfBiasScoreOverrideObject.objects.get(id=3)
        assert "deleted" in invalid.get_object_name()

    def test_get_orphan_relations(self):
        actual = RiskOfBiasScoreOverrideObject.get_orphan_relations()
        expected = dedent(
            """
            Found orphaned RiskOfBiasScoreOverrideObjects:
            id=3;score=16;obj_ct=49;obj_id=99999
            """
        ).strip()
        assert actual == expected


@pytest.mark.django_db
class TestRiskOfBias:
    def test_get_dp_export(self):
        assessment_id = 1
        study_id = 1
        _, scores_map = RiskOfBias.get_dp_export(assessment_id, [study_id], "animal")
        scores_qs = RiskOfBiasScore.objects.filter(
            riskofbias__study=study_id, riskofbias__final=True, riskofbias__active=True,
        )

        # all of the metrics are mapped
        assert set(scores_qs.values_list("metric_id", flat=True)) == {
            metric for _, metric in scores_map.keys()
        }

        # however, study has more scores than metrics
        assert scores_qs.count() > len(scores_map.keys())

        # make sure only default scores are used
        default_scores_qs = scores_qs.filter(is_default=True)
        expected_metric_to_score = {
            metric: score for metric, score in default_scores_qs.values_list("metric", "score")
        }
        for (_, metric), score in scores_map.items():
            expected_score = expected_metric_to_score[metric]
            assert json.loads(score)["sortValue"] == expected_score
