import pytest
from django.core.exceptions import ObjectDoesNotExist

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


@pytest.mark.django_db
class TestReference:
    @pytest.mark.vcr
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

    def test_has_study(self):
        # make sure our test-study checker works
        ref = Reference.objects.get(id=1)
        assert ref.has_study is True
        assert ref.study.id == 1

        ref = Reference.objects.get(id=3)
        assert ref.has_study is False
        with pytest.raises(ObjectDoesNotExist):
            ref.study.id

    def test_get_json(self):
        # make sure `get_json` works
        ref = Reference.objects.get(id=1)
        data = ref.get_json(json_encode=False)
        assert data["pk"] == 1
