import pytest

from hawc.apps.lit.models import Reference, ReferenceFilterTag


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


@pytest.mark.vcr
@pytest.mark.django_db
class TestReference:
    def test_update_hero_metadata(self, db_keys):
        # get initial data
        refs = Reference.objects.filter(
            id__in=[db_keys.reference_linked, db_keys.reference_unlinked]
        )
        old_titles = [ref.title for ref in refs]

        # ensure command is successful
        ret = Reference.update_hero_metadata(refs[0].assessment_id)
        assert ret.successful()

        # ensure references changed
        refs = refs.all()
        new_titles = [ref.title for ref in refs]
        assert old_titles != new_titles
