import pytest
from django.core.exceptions import ObjectDoesNotExist

from hawc.apps.assessment.models import HAWCUser
from hawc.apps.lit.models import Reference, ReferenceFilterTag, Search
from hawc.apps.study.models import Study


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

    def test_to_dict(self):
        # make sure `to_dict` works
        ref = Reference.objects.get(id=1)
        data = ref.to_dict()
        assert data["pk"] == 1

        data = ref.to_json()
        assert isinstance(data, str)

    def test_update_tags(self):
        # Test that conflict resolution is working
        ref = Reference.objects.get(id=9)
        pm = HAWCUser.objects.get(email="pm@hawcproject.org")
        tm = HAWCUser.objects.get(email="team@hawcproject.org")

        # User #1 adds user tags, but not applied to reference since we need 2+ people
        tags = [32]
        ref.update_tags(tags, pm)
        ref.refresh_from_db()
        assert ref.has_user_tag_conflicts() is True
        assert ref.tags.count() == 0

        # User #2 adds the same tags, those are now applied to the reference tag
        ref.update_tags(tags, tm)
        ref.refresh_from_db()
        assert ref.has_user_tag_conflicts() is False
        assert ref.tags.count() > 0

        # User #2 changes their tags, now there are conflicts again; the reference is unchanged
        new_tags = [33]
        ref.update_tags(new_tags, tm)
        ref.refresh_from_db()
        assert ref.has_user_tag_conflicts() is True
        assert list(ref.tags.values_list("id", flat=True)) == tags


@pytest.mark.vcr
@pytest.mark.django_db
class TestSearch:
    def test_delete_old_references(self):
        prior_search = Search.objects.first()
        tag = ReferenceFilterTag.objects.first()

        def create_search():
            s = Search.objects.create(
                assessment_id=1,
                title="test",
                slug="test",
                search_type="s",
                source=1,
                search_string="burritos school lunch",
            )
            # create a new search; ensure it returns 3 references
            # https://pubmed.ncbi.nlm.nih.gov/?term=burritos+school+lunch
            assert s.references.count() == 0
            s.run_new_query()
            assert s.references.count() == 3

            # now narrow the search; it will return fewer results that may need to be deleted
            # https://pubmed.ncbi.nlm.nih.gov/?term=burritos+school+lunch+gastrointestinal
            s.search_string = "burritos school lunch gastrointestinal"
            s.save()

            return s

        # narrow search; confirm that references are deleted
        search = create_search()
        search.run_new_query()
        assert search.references.count() == 2
        search.delete()

        # confirm tag guard works
        search = create_search()
        for ref in search.references.all():
            ref.tags.add(tag)
        search.run_new_query()
        assert search.references.count() == 3
        search.delete()

        # confirm search guard works
        search = create_search()
        for ref in search.references.all():
            ref.searches.add(prior_search)
        search.run_new_query()
        assert search.references.count() == 3
        search.delete()

        # confirm study guard works
        search = create_search()
        for ref in search.references.all():
            Study.save_new_from_reference(ref, {})
        search.run_new_query()
        assert search.references.count() == 3
        search.delete()
