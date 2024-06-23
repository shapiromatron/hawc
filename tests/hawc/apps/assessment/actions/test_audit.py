import pytest

from hawc.apps.assessment.actions.audit import AssessmentAuditSerializer, AuditType
from hawc.apps.assessment.models import Assessment


@pytest.mark.django_db
class TestAssessmentAuditSerializer:
    def test_export(self):
        # has ani, epiv1, assess, rob
        assess = Assessment.objects.get(id=2)
        ser = AssessmentAuditSerializer(assessment=assess, type=AuditType.ASSESSMENT)
        df = ser.get_df()
        assert df.shape[1] == 6

        ser = AssessmentAuditSerializer(assessment=assess, type=AuditType.ANIMAL)
        df = ser.get_df()
        assert df.shape[1] == 6

        ser = AssessmentAuditSerializer(assessment=assess, type=AuditType.EPI)
        df = ser.get_df()
        assert df.shape[1] == 6

        ser = AssessmentAuditSerializer(assessment=assess, type=AuditType.ROB)
        df = ser.get_df()
        assert df.shape[1] == 6

        # has epiv2
        assess = Assessment.objects.get(id=1)
        ser = AssessmentAuditSerializer(assessment=assess, type=AuditType.EPI)
        df = ser.get_df()
        assert df.shape[1] == 6
