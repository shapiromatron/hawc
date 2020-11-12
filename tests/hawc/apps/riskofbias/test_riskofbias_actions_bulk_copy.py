import re
from typing import Dict

import pytest

from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.request import Request

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore
from hawc.apps.riskofbias.actions.rob_clone import BulkRobCopy


@pytest.mark.django_db
class TestRiskOfBiasManager:
    def _valid_arguments(self, overrides: Dict = None) -> Request:
        data = {
            "src_assessment_id": 1,
            "dst_assessment_id": 2,
            "dst_author": HAWCUser.objects.get(email="pm@pm.com").id,
            "src_dst_study_ids": [(1, 5)],
            "src_dst_metric_ids": [(1, 14), (2, 15)],
            "copy_mode": 1,
            "author_mode": 1,
        }
        if overrides:
            data.update(overrides)
        factory = APIRequestFactory()
        view = APIView()
        request = view.initialize_request(factory.post("/", data, format="json"))
        return request

    # def test_bulk_copy_all(self, db_keys):
    #     kwargs = self._valid_arguments()
    #     _, mapping = RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all scores from src studies should be in mapping
    #     src_study_ids = mapping["study"].keys()
    #     src_score_ids = mapping["score"].keys()
    #     assert (
    #         len(src_score_ids)
    #         == RiskOfBiasScore.objects.filter(riskofbias__study__in=src_study_ids).count()
    #     )

    #     # all src scores should be copied
    #     score_ids = [item for pair in mapping["score"].items() for item in pair]
    #     score_id_to_instance = RiskOfBiasScore.objects.in_bulk(score_ids)
    #     for src_score_id, dst_score_id in mapping["score"].items():
    #         src_score = score_id_to_instance[src_score_id]
    #         dst_score = score_id_to_instance[dst_score_id]
    #         assert dst_score.score == src_score.score
    #         assert dst_score.metric_id == mapping["metric"][src_score.metric_id]
    #         assert dst_score.riskofbias_id == mapping["riskofbias"][src_score.riskofbias_id]

    #     # all riskofbiases from src studies should be in mapping
    #     src_riskofbias_ids = mapping["riskofbias"].keys()
    #     assert len(src_riskofbias_ids) == RiskOfBias.objects.filter(study__in=src_study_ids).count()

    #     # all src riskofbiases should be copied
    #     riskofbias_ids = [item for pair in mapping["riskofbias"].items() for item in pair]
    #     riskofbias_id_to_instance = RiskOfBias.objects.in_bulk(riskofbias_ids)
    #     for src_riskofbias_id, dst_riskofbias_id in mapping["riskofbias"].items():
    #         src_riskofbias = riskofbias_id_to_instance[src_riskofbias_id]
    #         dst_riskofbias = riskofbias_id_to_instance[dst_riskofbias_id]
    #         assert dst_riskofbias.final == src_riskofbias.final
    #         assert dst_riskofbias.active == src_riskofbias.active
    #         assert dst_riskofbias.study_id == mapping["study"][src_riskofbias.study_id]

    # def test_bulk_copy_final(self, db_keys):
    #     kwargs = self._valid_arguments()
    #     kwargs["copy_mode"] = 2
    #     kwargs["author_mode"] = 2
    #     _, mapping = RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all scores from src studies should be in mapping
    #     src_study_ids = mapping["study"].keys()
    #     src_score_ids = mapping["score"].keys()
    #     assert (
    #         len(src_score_ids)
    #         == RiskOfBiasScore.objects.filter(riskofbias__study__in=src_study_ids).count()
    #     )

    #     # all src scores should be copied
    #     score_ids = [item for pair in mapping["score"].items() for item in pair]
    #     score_id_to_instance = RiskOfBiasScore.objects.in_bulk(score_ids)
    #     for src_score_id, dst_score_id in mapping["score"].items():
    #         src_score = score_id_to_instance[src_score_id]
    #         dst_score = score_id_to_instance[dst_score_id]
    #         assert dst_score.score == src_score.score
    #         assert dst_score.metric_id == mapping["metric"][src_score.metric_id]
    #         assert dst_score.riskofbias_id == mapping["riskofbias"][src_score.riskofbias_id]

    #     # all riskofbiases from src studies should be in mapping
    #     src_riskofbias_ids = mapping["riskofbias"].keys()
    #     assert len(src_riskofbias_ids) == RiskOfBias.objects.filter(study__in=src_study_ids).count()

    #     # all src riskofbiases should be copied
    #     riskofbias_ids = [item for pair in mapping["riskofbias"].items() for item in pair]
    #     riskofbias_id_to_instance = RiskOfBias.objects.in_bulk(riskofbias_ids)
    #     for src_riskofbias_id, dst_riskofbias_id in mapping["riskofbias"].items():
    #         src_riskofbias = riskofbias_id_to_instance[src_riskofbias_id]
    #         dst_riskofbias = riskofbias_id_to_instance[dst_riskofbias_id]
    #         assert dst_riskofbias.final is False
    #         assert dst_riskofbias.active is True
    #         assert dst_riskofbias.study_id == mapping["study"][src_riskofbias.study_id]
    #         assert dst_riskofbias.author == kwargs["dst_author"]

    def test_validate_bulk_copy(self, db_keys):
        # assessments must be different
        request = self._valid_arguments(overrides=dict(dst_assessment_id=1))
        action = BulkRobCopy(request)
        action.validate()
        assert action.is_valid is False
        assert (
            "Source and destination assessments must be different"
            in action.errors["dst_assessment_id"]
        )

        # metric/study ids must be unique
        request = self._valid_arguments(overrides=dict(src_dst_metric_ids=[(2, 14), (2, 15)]))
        action = BulkRobCopy(request)
        action.validate()
        assert action.is_valid is False
        assert "Source metric ids must be unique" in action.errors["src_dst_metric_ids"]

    #     # all src studies from src assessment
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_study_ids"][0] = (-1, 5)
    #     expected_error = "Invalid source study"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all dst studies from dst assessment
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_study_ids"][0] = (1, -1)
    #     expected_error = "Invalid destination study"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all dst studies have no riskofbias
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_study_ids"][0] = (1, 7)
    #     expected_error = "Risk of bias data already exists"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all src metrics from src assessment
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_metric_ids"][0] = (14, 14)
    #     expected_error = "Invalid source metric"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all src study metrics in src metrics
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_metric_ids"] = [(1, 14)]
    #     expected_error = "Need mapping"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)

    #     # all dst metrics from dst assessment
    #     kwargs = self._valid_arguments()
    #     kwargs["src_dst_metric_ids"][0] = (1, 1)
    #     expected_error = "Invalid destination metric"
    #     with pytest.raises(ValidationError, match=re.escape(expected_error)):
    #         RiskOfBias.objects.bulk_copy(**kwargs)
