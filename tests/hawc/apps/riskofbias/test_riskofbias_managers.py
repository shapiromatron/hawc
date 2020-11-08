import json
import re

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Log
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore
from hawc.apps.study.models import Study


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
        # TODO test actual instances

        assert True

    def test_bulk_copy_final(self, db_keys):
        kwargs = self._valid_arguments()
        kwargs["final_only"] = True
        _, mapping = RiskOfBias.objects.bulk_copy(**kwargs)
        # TODO test actual instances

        assert True

    def test_validate_bulk_copy(self, db_keys):
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
