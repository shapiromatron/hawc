import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.epiv2.exports import EpiFlatComplete
from hawc.apps.epiv2.models import DataExtraction


@pytest.mark.django_db
class TestEpiFlatComplete:
    def test_export(self):
        assessment = Assessment.objects.get(id=1)
        qs = DataExtraction.objects.filter(design__study__assessment_id=1)
        assert qs.count() > 0
        exporter = EpiFlatComplete(qs, assessment=assessment, filename="fn")
        df = exporter.build_df()
        assert df.shape == (12, 118)
