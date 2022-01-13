import pytest

from hawc.apps.epi import models


@pytest.mark.django_db
def test_heatmap_df(db_keys):
    df = models.Result.heatmap_df(db_keys.assessment_final, True)
    expected_columns = [
        "study id",
        "study citation",
        "study identifier",
        "overall study evaluation",
        "study population id",
        "study population name",
        "study population source",
        "study design",
        "comparison set id",
        "comparison set name",
        "exposure id",
        "exposure name",
        "exposure route",
        "exposure measure",
        "exposure metric",
        "outcome id",
        "outcome name",
        "system",
        "effect",
        "effect subtype",
        "result id",
        "result name",
    ]
    assert df.columns.tolist() == expected_columns
