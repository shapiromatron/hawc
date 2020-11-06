import pytest
from rest_framework.test import APIClient

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.assessment.models import Log
from hawc.apps.riskofbias.models import (
    RiskOfBias,
    RiskOfBiasScore,
)
from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestRiskOfBiasManager:
    def test_bulk_copy_all(self, db_keys):
        src_assessment_id = 1
        dst_assessment_id = 2
        dst_author = HAWCUser.objects.get(email="pm@pm.com")
        src_dst_study_ids = [(1, 5)]
        src_dst_metric_ids = [(1, 14), (2, 15)]
        final_only = False
        log_id = RiskOfBias.objects.bulk_copy(
            src_assessment_id,
            dst_assessment_id,
            dst_author,
            src_dst_study_ids,
            src_dst_metric_ids,
            final_only,
        )
        import pdb

        pdb.set_trace()
        assert True

    def test_bulk_copy_final(self, db_keys):

        assert True

    def test_validate_bulk_copy(self, db_keys):
        # all src studies from src assessment

        # all dst studies from dst assessment

        # all src metrics from src assessment

        # all dst metrics from dst assessment

        # all dst studies have no riskofbias

        # all users who authored src riskofbiases are team member
        # or higher on dst assessment
        assert True
