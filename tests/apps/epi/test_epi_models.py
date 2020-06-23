import pytest

from hawc.apps.animal import models


@pytest.mark.django_db
def test_heatmap_df(db_keys):
    df = models.Result.heatmap_df(db_keys.assessment_final, True)
    expected_columns = [
        "result id",
        "result name",
        "outcome id",
        "system",
        "effect",
        "effect_subtype",
        "comparison set id",
        "comparison set name",
        "exposure id",
        "exposure name",
        "study population id",
        "study population name",
        "study design",
        "study id",
        "study citation",
        "study identifier",
    ]
    assert df.columns.tolist().sort() == expected_columns.sort()
