import json

import pytest

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.actions.rob_clone import BulkCopyAuthor, BulkCopyMode, BulkRobCopyAction
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore


@pytest.mark.django_db
class TestBulkRobCopyAction:
    def _valid_arguments(self) -> dict:
        return {
            "src_assessment_id": 1,
            "dst_assessment_id": 2,
            "dst_author_id": HAWCUser.objects.get(email="team@hawcproject.org").id,
            "src_dst_study_ids": [(1, 5)],
            "src_dst_metric_ids": [(1, 14), (2, 15)],
            "copy_mode": BulkCopyMode.ALL_ACTIVE,
            "author_mode": BulkCopyAuthor.PRESERVE_ORIGINAL,
        }

    def test_validation(self):
        invalid_datasets = [
            # data structure
            (dict(src_dst_study_ids="not a list"), "Input should be a valid list"),
            (dict(src_dst_study_ids=[(-1,)]), "Field required"),
            (
                dict(src_dst_study_ids=[(-1, -1, -1)]),
                "Tuple should have at most 2 items after validation",
            ),
            # business logic
            (dict(dst_assessment_id=1), "Source and destination assessments must be different"),
            (dict(src_dst_study_ids=[(-1, 5)]), "Invalid source study"),
            (dict(src_dst_study_ids=[(1, -1)]), "Invalid destination study"),
            (dict(src_dst_metric_ids=[(2, 14), (2, 15)]), "Source metric ids must be unique"),
            (dict(src_dst_metric_ids=[(14, 14)]), "Invalid source metric"),
            (dict(src_dst_metric_ids=[(1, 14)]), "Need mapping"),
            (dict(src_dst_metric_ids=[(1, 1)]), "Invalid destination metric"),
            (
                dict(dst_author_id=None, author_mode=BulkCopyAuthor.OVERWRITE),
                "dst_author_id required when author_mode overwrite.",
            ),
            (
                dict(dst_author_id=-1, author_mode=BulkCopyAuthor.OVERWRITE),
                "Author not found.",
            ),
        ]
        for overrides, error_msg in invalid_datasets:
            data = self._valid_arguments()
            data.update(overrides)
            action = BulkRobCopyAction(data)
            action.validate()
            assert action.is_valid is False
            assert error_msg in json.dumps(action.errors)

    def test_copy_all(self):
        data = self._valid_arguments()
        data.update(copy_mode=BulkCopyMode.ALL_ACTIVE, author_mod=BulkCopyAuthor.PRESERVE_ORIGINAL)

        action = BulkRobCopyAction(data)
        action.validate()
        assert action.is_valid is True
        res = action.evaluate()
        mapping = res["mapping"]

        # all scores from src studies should be in mapping
        src_study_ids = mapping["study"].keys()
        src_score_ids = mapping["score"].keys()
        assert (
            len(src_score_ids)
            == RiskOfBiasScore.objects.filter(
                riskofbias__active=True, riskofbias__study__in=src_study_ids
            ).count()
        )

        # all riskofbiases from src studies should be in mapping
        src_riskofbias_ids = mapping["riskofbias"].keys()
        assert (
            len(src_riskofbias_ids)
            == RiskOfBias.objects.filter(active=True, study__in=src_study_ids).count()
        )

        # all src riskofbiases should be copied
        riskofbias_ids = [item for pair in mapping["riskofbias"].items() for item in pair]
        riskofbias_id_to_instance = RiskOfBias.objects.in_bulk(riskofbias_ids)
        for src_riskofbias_id, dst_riskofbias_id in mapping["riskofbias"].items():
            src_riskofbias = riskofbias_id_to_instance[src_riskofbias_id]
            dst_riskofbias = riskofbias_id_to_instance[dst_riskofbias_id]
            # check study changed but original author is preserved
            assert dst_riskofbias.study_id == mapping["study"][src_riskofbias.study_id]
            assert dst_riskofbias.author_id == src_riskofbias.author_id

        # all src scores should be copied
        score_ids = [item for pair in mapping["score"].items() for item in pair]
        score_id_to_instance = RiskOfBiasScore.objects.in_bulk(score_ids)
        for src_score_id, dst_score_id in mapping["score"].items():
            src_score = score_id_to_instance[src_score_id]
            dst_score = score_id_to_instance[dst_score_id]
            assert dst_score.score == src_score.score
            assert dst_score.metric_id == mapping["metric"][src_score.metric_id]
            assert dst_score.riskofbias_id == mapping["riskofbias"][src_score.riskofbias_id]

    def test_copy_final_to_initial(self):
        data = self._valid_arguments()
        data.update(copy_mode=BulkCopyMode.FINAL_TO_INITIAL, author_mode=BulkCopyAuthor.OVERWRITE)

        action = BulkRobCopyAction(data)
        action.validate()
        assert action.is_valid is True
        res = action.evaluate()
        mapping = res["mapping"]

        # all src riskofbiases should be copied
        rob_ids = [item for pair in mapping["riskofbias"].items() for item in pair]  # flatten
        rob_map = RiskOfBias.objects.in_bulk(rob_ids)
        for src_rob_id, dst_rob_id in mapping["riskofbias"].items():
            src_riskofbias = rob_map[src_rob_id]
            dst_riskofbias = rob_map[dst_rob_id]
            assert dst_riskofbias.study_id == mapping["study"][src_riskofbias.study_id]

            # ensure final is changed
            assert src_riskofbias.final is True and dst_riskofbias.active is True
            assert dst_riskofbias.final is False and dst_riskofbias.active is True

            # ensure author is overridden
            assert src_riskofbias.author_id != dst_riskofbias.author_id
            assert dst_riskofbias.author_id == data["dst_author_id"]

        # all src scores should be copied
        score_ids = [item for pair in mapping["score"].items() for item in pair]
        score_map = RiskOfBiasScore.objects.in_bulk(score_ids)
        for src_score_id, dst_score_id in mapping["score"].items():
            src_score = score_map[src_score_id]
            dst_score = score_map[dst_score_id]
            assert dst_score.score == src_score.score
            assert dst_score.metric_id == mapping["metric"][src_score.metric_id]
            assert dst_score.riskofbias_id == mapping["riskofbias"][src_score.riskofbias_id]
