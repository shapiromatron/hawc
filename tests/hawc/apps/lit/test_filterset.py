import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit.filterset import ReferenceFilterSet
from hawc.apps.lit.models import Reference, ReferenceFilterTag

from ..test_utils import mock_request


@pytest.mark.django_db
class TestReferenceFilterSet:
    def test_authors(self, db_keys):
        request = mock_request(role="pm")
        assessment = Assessment.objects.get(id=db_keys.assessment_final)
        qs = Reference.objects.filter(assessment=assessment)
        author = qs.first().authors_short[:5]
        fs = ReferenceFilterSet(
            data={"authors": author}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() >= 1

    def test_search(self, db_keys):
        request = mock_request(role="pm")
        assessment = Assessment.objects.get(id=db_keys.assessment_final)
        qs = Reference.objects.filter(assessment=assessment)
        fs = ReferenceFilterSet(
            data={"search": 2}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() == 1

    def test_tags(self, db_keys):
        request = mock_request(role="pm")
        assessment = Assessment.objects.get(id=db_keys.assessment_final)
        qs = Reference.objects.filter(assessment=assessment)
        fs = ReferenceFilterSet(
            data={"tags": "untagged"}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.qs.count() > 0

        root_tag = ReferenceFilterTag.get_assessment_root(assessment.pk)
        left_tag = root_tag.get_first_child()
        fs = ReferenceFilterSet(
            data={"tags": [left_tag.pk], "include_descendants": True},
            assessment=assessment,
            queryset=qs,
            request=request,
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

    def test_anything_tagged(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_final)
        request = mock_request(role="pm")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"anything_tagged": True}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

    def test_my_tags(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"my_tags": ["untagged"]}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

        root_tag = ReferenceFilterTag.get_assessment_root(assessment.pk)
        left_tag = root_tag.get_first_child()
        fs = ReferenceFilterSet(
            data={"tags": [left_tag.pk], "include_descendants": True},
            assessment=assessment,
            queryset=qs,
            request=request,
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

    def test_anything_tagged_me(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"anything_tagged_me": True}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

    def test_tag_additions(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)
        root_tag = ReferenceFilterTag.get_assessment_root(assessment.pk)
        left_tag = root_tag.get_first_child()

        fs = ReferenceFilterSet(
            data={"addition_tags": [left_tag.pk], "include_additiontag_descendants": True},
            assessment=assessment,
            queryset=qs,
            request=request,
        )
        assert fs.errors == {}
        assert fs.qs.count() == 1
        assert fs.qs.first().pk == db_keys.reference_tag_conflict

    def test_tag_deletions(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)
        root_tag = ReferenceFilterTag.get_assessment_root(assessment.pk)
        left_tag = root_tag.get_first_child()

        fs = ReferenceFilterSet(
            data={"deletion_tags": [left_tag.pk], "include_deletiontag_descendants": False},
            assessment=assessment,
            queryset=qs,
            request=request,
        )
        assert fs.errors == {}
        assert fs.qs.count() == 0

    def test_partially_tagged(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"partially_tagged": True}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() == 0

    def test_needs_tagging(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"needs_tagging": True}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() > 0

    def test_workflow(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_conflict_resolution)
        request = mock_request(role="team")
        qs = Reference.objects.filter(assessment=assessment)

        fs = ReferenceFilterSet(
            data={"workflow": 1}, assessment=assessment, queryset=qs, request=request
        )
        assert fs.errors == {}
        assert fs.qs.count() == 0
