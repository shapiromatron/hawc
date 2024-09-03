import pytest

# use concrete implementations to test
from hawc.apps.animal.models import DoseGroup, Experiment
from hawc.apps.common.models import (
    apply_flavored_help_text,
    clone_name,
    sql_format,
    sql_query_to_dicts,
)
from hawc.apps.epiv2.models import ExposureLevel
from hawc.apps.lit.models import ReferenceFilterTag
from hawc.apps.riskofbias import models

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
class TestAssessmentRootMixin:
    def test__annotate_nested_names(self, db_keys):
        qs = ReferenceFilterTag.get_assessment_qs(db_keys.assessment_working)
        ReferenceFilterTag.annotate_nested_names(qs)
        names = [el.nested_name for el in qs]
        assert names == _nested_names

    def test_as_dataframe(self, db_keys):
        df = ReferenceFilterTag.as_dataframe(db_keys.assessment_working)
        assert df.nested_name.values.tolist() == _nested_names

    def test_clean_orphans(self, db_keys):
        n = ReferenceFilterTag.objects.all().count()
        assert ReferenceFilterTag.objects.filter(id=40, name="Orphan").exists()
        ReferenceFilterTag.clean_orphans()
        assert not ReferenceFilterTag.objects.filter(id=40, name="Orphan").exists()
        assert ReferenceFilterTag.objects.all().count() == n - 1


@pytest.mark.django_db
class TestBaseManager:
    def test_get_order_by(self):
        assert Experiment._meta.ordering == []
        assert Experiment.objects._get_order_by() == ("id",)
        assert DoseGroup._meta.ordering == ("dose_units", "dose_group_id")
        assert DoseGroup.objects._get_order_by() == ("dose_units", "dose_group_id")


def test_sql_format():
    assert str(sql_format("/left/{}", "foo")) == "Concat(ConcatPair(Value('/left/'), F(foo)))"
    assert str(sql_format("{}/right", "foo")) == "Concat(ConcatPair(F(foo), Value('/right')))"
    assert (
        str(sql_format("/test/{}/here/", "foo"))
        == "Concat(ConcatPair(Value('/test/'), ConcatPair(F(foo), Value('/here/'))))"
    )
    assert (
        str(sql_format("/a/{}/b/{}/c/", "foo", "bar"))
        == "Concat(ConcatPair(Value('/a/'), ConcatPair(F(foo), ConcatPair(Value('/b/'), ConcatPair(F(bar), Value('/c/'))))))"
    )

    for case in ["/too-few/", "{}", "/too-many/{}/{}/"]:
        with pytest.raises(ValueError):
            sql_format(case, "foo")


def test_apply_flavored_help_text(settings):
    settings.MODIFY_HELP_TEXT = True
    settings.HAWC_FLAVOR = "EPA"
    initial = models.RiskOfBiasAssessment._meta.get_field("help_text").help_text
    apply_flavored_help_text("riskofbias")
    changed = models.RiskOfBiasAssessment._meta.get_field("help_text").help_text
    assert initial != changed


def test_clone_name():
    m = ExposureLevel(name="a")
    assert clone_name(m, "name") == "a (2)"
    m.name = "b (2)"
    assert clone_name(m, "name") == "b (3)"
    m.name = "c" * 64
    assert clone_name(m, "name") == ("c" * 60) + " (2)"
    m.name = "c" * 60 + " (9)"
    assert len(m.name) == 64
    assert clone_name(m, "name") == ("c" * 59) + " (10)"


@pytest.mark.django_db
def test_sql_query_to_dicts():
    query = "SELECT id, name FROM assessment_assessment ORDER BY id LIMIT %s "
    results = sql_query_to_dicts(query, (2,))
    assert list(results) == [{"id": 1, "name": "Chemical Z"}, {"id": 2, "name": "Chemical X"}]
