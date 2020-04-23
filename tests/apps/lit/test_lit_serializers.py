import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit.models import Reference, ReferenceTags
from hawc.apps.lit.serializers import BulkReferenceTagSerializer


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
