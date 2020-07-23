import pytest
from rest_framework.serializers import ValidationError

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit.models import Reference, ReferenceTags
from hawc.apps.lit.serializers import (
    BulkReferenceTagSerializer,
    ReferenceReplaceHeroIdSerializer,
    ReferenceUpdateSerializer,
)


@pytest.mark.django_db
def test_BulkReferenceTagSerializer(db_keys):
    context = {"assessment": Assessment.objects.get(id=db_keys.assessment_working)}

    # check validation errors
    data = {"operation": "append", "csv": "nope"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == 'Invalid column headers; expecting "reference_id,tag_id"'

    data = {"operation": "append", "csv": "reference_id,tag_id"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "CSV has no data"

    # reference_id 2 is from db_keys.assessment_final
    data = {"operation": "append", "csv": "reference_id,tag_id\n2,2"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "All reference ids are not from assessment 1"

    # tag_id 11 is from db_keys.assessment_final
    data = {"operation": "append", "csv": "reference_id,tag_id\n1,11"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "All tag ids are not from assessment 1"

    # invalid ids
    data = {"operation": "append", "csv": "reference_id,tag_id\n-1,-1"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "All reference ids are not from assessment 1"

    # check success
    reference = Reference.objects.get(id=db_keys.study_working)
    assert reference.tags.count() == 0

    data = {"operation": "append", "csv": "reference_id,tag_id\n1,2"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()

    reference.refresh_from_db()
    assert reference.tags.count() == 1

    # check append
    data = {"operation": "append", "csv": "reference_id,tag_id\n1,3"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    reference.refresh_from_db()
    assert reference.tags.count() == 2

    # check replace
    data = {"operation": "replace", "csv": "reference_id,tag_id\n1,4"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    reference.refresh_from_db()
    assert reference.tags.count() == 1
    reference.tags.all()[0].id == 4

    # check duplicates
    data = {"operation": "replace", "csv": "reference_id,tag_id\n1,3\n1,3"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "CSV contained duplicates; please remove before importing"

    # check that a 2x2 table works
    csv = "reference_id,tag_id\n1,3\n1,4\n3,3\n3,4\n"
    data = {"operation": "replace", "csv": csv}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    assert (
        ReferenceTags.objects.as_dataframe(db_keys.assessment_working).to_csv(
            index=False, line_terminator="\n"
        )
        == csv
    )


@pytest.mark.vcr
@pytest.mark.django_db
class TestReferenceUpdateSerializer:
    def test_valid(self, db_keys):
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        serializer = ReferenceUpdateSerializer(data={"replace": refs})
        assert serializer.is_valid() is False

        ret = serializer.execute()
        assert ret.successful()

        assert refs[0].title == "Early lung events following low-dose asbestos exposure"
        assert (
            refs[1].title
            == "Asbestos-induced lung injury in the sheep model: the initial alveolitis"
        )


@pytest.mark.vcr
@pytest.mark.django_db
class TestReferenceReplaceHeroIdSerializer:
    # TODO - rewrite
    def test_valid(self, db_keys):
        """
        For a valid case we'll test a HERO ID swap
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        replace = [
            [refs[0].id, int(refs[1].identifiers.get(database=2).unique_id)],
            [refs[1].id, int(refs[0].identifiers.get(database=2).unique_id)],
        ]
        serializer = ReferenceReplaceHeroIdSerializer(
            refs, many=True, allow_empty=False, context={"replace": replace}
        )

        ret = serializer.execute()
        assert ret.successful()

        assert (
            refs[0].title
            == "Asbestos-induced lung injury in the sheep model: the initial alveolitis"
        )
        assert refs[1].title == "Early lung events following low-dose asbestos exposure"

    def test_duplicate(self, db_keys):
        """
        Test a replace that will result in two references with
        the same HERO ID
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        replace = [[refs[0].id, refs[1].identifiers.get(database=2).unique_id]]
        serializer = ReferenceReplaceHeroIdSerializer(
            refs, many=True, allow_empty=False, context={"replace": replace}
        )

        with pytest.raises(ValidationError) as err:
            serializer.execute()

        assert err.value.args[0] == "Duplicate HERO references."

    def test_bad_hero(self, db_keys):
        """
        Test a replace where one of the HERO IDs are invalid.
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        replace = [[refs[0].id, -1]]
        serializer = ReferenceReplaceHeroIdSerializer(
            refs, many=True, allow_empty=False, context={"replace": replace}
        )

        with pytest.raises(ValidationError) as err:
            serializer.execute()

        assert (
            err.value.args[0] == "Import failed; the following HERO IDs could not be imported: -1"
        )

    def test_bad_ref(self, db_keys):
        """
        Test a replace where one of the ref IDs are are not in the queryset.
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        invalid_ref = Reference.objects.all().difference(refs).first()
        replace = [[invalid_ref.id, 1]]
        serializer = ReferenceReplaceHeroIdSerializer(
            refs, many=True, allow_empty=False, context={"replace": replace}
        )

        with pytest.raises(ValidationError) as err:
            serializer.execute()

        assert err.value.args[0] == "All references must be from selected assessment."
