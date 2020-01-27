import pytest

from hawc.apps.lit.models import ReferenceFilterTag


@pytest.mark.django_db
def test_clean_import_string(db_keys):
    df = ReferenceFilterTag.as_dataframe(db_keys.assessment_working)
    assert df.nested_name.values.tolist() == [
        "Inclusion",
        "Inclusion|Human Study",
        "Inclusion|Animal Study",
        "Inclusion|Mechanistic Study",
        "Exclusion",
        "Exclusion|Tier I",
        "Exclusion|Tier II",
        "Exclusion|Tier III",
        "Exclusion|Tier III|a",
        "Exclusion|Tier III|b",
        "Exclusion|Tier III|c",
    ]
