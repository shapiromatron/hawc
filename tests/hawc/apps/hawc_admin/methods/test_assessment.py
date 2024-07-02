import pandas as pd
import pytest
from pandas.io.formats.style import Styler
from plotly.graph_objs import Figure

from hawc.apps.assessment.models import Assessment
from hawc.apps.hawc_admin.methods import assessment


@pytest.mark.django_db
def test_growth_matrix():
    df = assessment.growth_matrix(days=3650)
    assert isinstance(df, Styler)
    assert isinstance(df.data, pd.DataFrame)


@pytest.mark.django_db
class TestAssessmentGrowthSettings:
    def test_time_series(self):
        form = assessment.AssessmentGrowthSettings(
            data={"assessment_id": 1, "grouper": "A", "log": True}
        )
        assert form.is_valid()
        assess, fig = form.time_series()
        assert isinstance(assess, Assessment)
        assert assess.id == 1
        assert isinstance(fig, Figure)
