import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.summary.filterset import SummaryTableFilterSet, VisualFilterSet
from hawc.apps.summary.models import SummaryTable, Visual

from ..test_utils import mock_request


@pytest.mark.django_db
class TestVisualFilterSet:
    def test_label(self):
        request = mock_request(role="pm")
        assessment = Assessment.objects.get(id=1)
        qs = Visual.objects.filter(assessment_id=1)
        fs = VisualFilterSet(
            data={"label": [2]}, assessment=assessment, queryset=qs, request=request
        )
        assert qs.count() == 2
        assert fs.qs.count() == 1


@pytest.mark.django_db
class TestSummaryTableFilterSet:
    def test_label(self):
        request = mock_request(role="pm")
        assessment = Assessment.objects.get(id=1)
        qs = SummaryTable.objects.filter(assessment_id=1)
        fs = SummaryTableFilterSet(
            data={"label": [2]}, assessment=assessment, queryset=qs, request=request
        )
        assert qs.count() == 3
        assert fs.qs.count() == 1
