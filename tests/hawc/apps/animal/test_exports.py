import pandas as pd

from hawc.apps.animal import exports


def test_handle_treatment_period():
    expected = [
        ("1-generation reproductive", "", "1-generation reproductive"),
        ("Short-term (1-30 days)", "", "short-term "),
        ("Short-term (1-30 days)", "30 days", "short-term  (30 days)"),
    ]
    df = pd.DataFrame(
        data=expected,
        columns=["experiment-type_display", "dosing_regime-duration_exposure_text", "tmp"],
    )
    expected_output = df["tmp"].tolist()
    df = df.drop(columns=["tmp"])
    df2 = exports.handle_treatment_period(df)
    assert df2["treatment period"].to_list() == expected_output
