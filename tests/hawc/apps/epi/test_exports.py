import pandas as pd
import pytest
from numpy import nan
from pandas.testing import assert_frame_equal

from hawc.apps.epi import exports
from hawc.apps.epi.models import Outcome


@pytest.mark.django_db
class TestOutcomeDataPivot:
    def test_add_ci(self):
        # two tuples, one is inputs, one is expected outputs
        # inputs: (lower_ci, upper_ci, n, estimate, variance, variance_type)
        # expected outputs: (lower_ci, upper_ci)
        data = [
            # keep entered values instead of calculating
            ((1.0, 2.0, None, None, None, ""), (1.0, 2.0)),
            ((1.0, None, None, None, None, ""), (1.0, None)),
            ((None, 2.0, None, None, None, ""), (None, 2.0)),
            ((1.0, 2.0, 10, 30, 2, "SD"), (1.0, 2.0)),
            # calculate
            ((None, None, 1, 30, 2, "SD"), (4.59, 55.41)),
            ((None, None, 10, 30, 2, "SD"), (28.56, 31.43)),
            ((None, None, 10, 30, 2, "SE"), (25.48, 34.52)),
            # ok bad cases
            ((None, None, None, None, None, "bad"), (None, None)),
            ((None, None, 10, 30, 2, "bad"), (None, None)),
        ]
        input_df = pd.DataFrame(
            data=[el1 for el1, _ in data],
            columns=[
                "result_group-lower_ci",
                "result_group-upper_ci",
                "result_group-n",
                "result_group-estimate",
                "result_group-variance",
                "result-variance_type",
            ],
        ).replace({nan: None})
        expected_df = pd.DataFrame(
            data=[el2 for _, el2 in data],
            columns=["result_group-lower_ci", "result_group-upper_ci"],
        )

        exporter = exports.OutcomeDataPivot(queryset=Outcome.objects.none())
        output_df = exporter._add_ci(input_df)[["result_group-lower_ci", "result_group-upper_ci"]]
        assert_frame_equal(output_df, expected_df, atol=0.01)
