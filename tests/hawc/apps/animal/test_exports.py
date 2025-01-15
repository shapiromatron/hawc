import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from hawc.apps.animal import exports
from hawc.apps.animal.models import Endpoint


@pytest.mark.django_db
class TestEndpointFlatDataPivot:
    def test_handle_treatment_period(self):
        # list of tuples, first is inputs, second is outputs
        # inputs: (type_display, duration_exposure_text)
        # expected outputs: treatment period
        expected = [
            (("1-generation reproductive", ""), "1-generation reproductive"),
            (("Short-term (1-30 days)", ""), "short-term"),
            (("Short-term (1-30 days)", "30 days"), "short-term (30 days)"),
        ]
        df = pd.DataFrame(
            data=[el[0] for el in expected],
            columns=["experiment-type_display", "dosing_regime-duration_exposure_text"],
        )
        expected_output = pd.Series(data=[el[1] for el in expected], name="treatment period")

        exporter = exports.EndpointFlatDataPivot(queryset=Endpoint.objects.none())
        df2 = exporter.handle_treatment_period(df)
        assert_series_equal(df2["treatment period"], expected_output)


def test_rename_udf_cols():
    df = pd.DataFrame(
        data=[[1] * 4], columns=["a", "b b", "b_udfs-content-field-b", "c_udfs-content-field-c"]
    )
    df = exports.rename_udf_cols(df)
    assert df.columns.tolist() == ["a", "b b", "b udf b", "c c"]
