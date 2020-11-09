import re

import pytest
from django.core.exceptions import ValidationError

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore


@pytest.mark.django_db
class TestRiskOfBiasManager:
    def _valid_arguments(self):
        return {
            "src_assessment_id": 1,
            "dst_assessment_id": 2,
            "dst_author": HAWCUser.objects.get(email="pm@pm.com"),
            "src_dst_study_ids": [(1, 5)],
            "src_dst_metric_ids": [(1, 14), (2, 15)],
            "final_only": False,
        }

    def test_bulk_copy_all(self, db_keys):
        kwargs = self._valid_arguments()
        _, mapping = RiskOfBias.objects.bulk_copy(**kwargs)

        # all scores from src studies should be in mapping
        src_study_ids = mapping["study"].keys()
        src_score_ids = mapping["score"].keys()
        assert (
            len(src_score_ids)
            == RiskOfBiasScore.objects.filter(riskofbias__study__in=src_study_ids).count()
        )

        # all src scores should be copied
        score_ids = [item for pair in mapping["score"].items() for item in pair]
        score_id_to_instance = RiskOfBiasScore.objects.in_bulk(score_ids)
        for src_score_id, dst_score_id in mapping["score"].items():
            src_score = score_id_to_instance[src_score_id]
            dst_score = score_id_to_instance[dst_score_id]
            assert dst_score.score == src_score.score
            assert dst_score.metric_id == mapping["metric"][src_score.metric_id]
            assert dst_score.riskofbias_id == mapping["riskofbias"][src_score.riskofbias_id]

        # all riskofbiases from src studies should be in mapping
        src_riskofbias_ids = mapping["riskofbias"].keys()
        assert len(src_riskofbias_ids) == RiskOfBias.objects.filter(study__in=src_study_ids).count()

        # all src riskofbiases should be copied
        riskofbias_ids = [item for pair in mapping["riskofbias"].items() for item in pair]
        riskofbias_id_to_instance = RiskOfBias.objects.in_bulk(riskofbias_ids)
        for src_riskofbias_id, dst_riskofbias_id in mapping["riskofbias"].items():
            src_riskofbias = riskofbias_id_to_instance[src_riskofbias_id]
            dst_riskofbias = riskofbias_id_to_instance[dst_riskofbias_id]
            assert dst_riskofbias.final == src_riskofbias.final
            assert dst_riskofbias.active == src_riskofbias.active
            assert dst_riskofbias.study_id == mapping["study"][src_riskofbias.study_id]
            assert dst_riskofbias.author == kwargs["dst_author"]

    def test_bulk_copy_final(self, db_keys):
        kwargs = self._valid_arguments()
        kwargs["final_only"] = True
        _, mapping = RiskOfBias.objects.bulk_copy(**kwargs)
        # TODO test actual instances

        assert True

    def test_validate_bulk_copy(self, db_keys):
        # assessments must be different
        kwargs = self._valid_arguments()
        kwargs["dst_assessment_id"] = 1
        expected_error = "Source and destination assessments must be different"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # metric/study ids must be unique
        kwargs = self._valid_arguments()
        kwargs["src_dst_metric_ids"][0] = (2, 14)
        expected_error = "Source metric ids must be unique"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all src studies from src assessment
        kwargs = self._valid_arguments()
        kwargs["src_dst_study_ids"][0] = (-1, 5)
        expected_error = "Invalid source study"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all dst studies from dst assessment
        kwargs = self._valid_arguments()
        kwargs["src_dst_study_ids"][0] = (1, -1)
        expected_error = "Invalid destination study"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all dst studies have no riskofbias
        kwargs = self._valid_arguments()
        kwargs["src_dst_study_ids"][0] = (1, 7)
        expected_error = "Risk of bias data already exists"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all src metrics from src assessment
        kwargs = self._valid_arguments()
        kwargs["src_dst_metric_ids"][0] = (14, 14)
        expected_error = "Invalid source metric"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all src study metrics in src metrics
        kwargs = self._valid_arguments()
        kwargs["src_dst_metric_ids"] = [(1, 14)]
        expected_error = "Need mapping"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all dst metrics from dst assessment
        kwargs = self._valid_arguments()
        kwargs["src_dst_metric_ids"][0] = (1, 1)
        expected_error = "Invalid destination metric"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            RiskOfBias.objects.bulk_copy(**kwargs)

        # all users who authored src riskofbiases are team member
        # or higher on dst assessment
        # TODO
