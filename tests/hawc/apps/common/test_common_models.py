import pytest

# use a concrete implementation to test AssessmentRootMixin
from hawc.apps.lit.models import ReferenceFilterTag

_nested_names = [
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


@pytest.mark.django_db
def test_AssessmentRootMixin_annotate_nested_names(db_keys):
    qs = ReferenceFilterTag.get_assessment_qs(db_keys.assessment_working)
    ReferenceFilterTag.annotate_nested_names(qs)
    names = [el.nested_name for el in qs]
    assert names == _nested_names


@pytest.mark.django_db
def test_AssessmentRootMixin_as_dataframe(db_keys):
    df = ReferenceFilterTag.as_dataframe(db_keys.assessment_working)
    assert df.nested_name.values.tolist() == _nested_names
