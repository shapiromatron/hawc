import re

import pytest
from rest_framework import exceptions

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit import constants
from hawc.apps.lit.models import Reference, ReferenceTags
from hawc.apps.lit.serializers import (
    BulkReferenceTagSerializer,
    FilterReferences,
    ReferenceReplaceHeroIdSerializer,
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

    # missing reference
    data = {"operation": "append", "csv": "reference_id,tag_id\n1,2\n-1,2"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is False
    assert serializer.errors["csv"][0] == "Reference(s) not found: {-1}"

    # check success
    reference = Reference.objects.get(id=db_keys.study_working)
    assert reference.tags.count() == 0

    data = {"operation": "append", "csv": "reference_id,tag_id\n1,2"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()

    reference.refresh_from_db()
    assert reference.tags.count() == 1

    # check dry run
    data = {"operation": "append", "csv": "reference_id,tag_id\n1,3", "dry_run": True}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    reference.refresh_from_db()
    assert reference.tags.count() == 1

    # check append
    data.pop("dry_run")
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    reference.refresh_from_db()
    assert reference.tags.count() == 2

    # check remove (non matches will be ignored)
    data = {"operation": "remove", "csv": "reference_id,tag_id\n1,3\n1,4"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    reference.refresh_from_db()
    assert reference.tags.count() == 1
    assert reference.tags.all()[0].id == 2

    # check replace
    data = {"operation": "replace", "csv": "reference_id,tag_id\n1,4"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    resp = ReferenceTags.objects.as_dataframe(db_keys.assessment_working).to_csv(
        index=False, lineterminator="\n"
    )
    assert resp == "reference_id,tag_id\n1,4\n"

    # check duplicates
    data = {"operation": "replace", "csv": "reference_id,tag_id\n1,3\n1,3"}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()

    reference.refresh_from_db()
    resp = ReferenceTags.objects.as_dataframe(db_keys.assessment_working).to_csv(
        index=False, lineterminator="\n"
    )
    assert resp == "reference_id,tag_id\n1,3\n"

    # check that a 2x2 table works
    csv = "reference_id,tag_id\n1,3\n1,4\n3,3\n3,4\n"
    data = {"operation": "replace", "csv": csv}
    serializer = BulkReferenceTagSerializer(data=data, context=context)
    assert serializer.is_valid() is True
    serializer.bulk_create_tags()
    resp = ReferenceTags.objects.as_dataframe(db_keys.assessment_working).to_csv(
        index=False, lineterminator="\n"
    )
    assert resp == csv


@pytest.mark.vcr
@pytest.mark.django_db
class TestReferenceReplaceHeroIdSerializer:
    def test_valid_new_ids(self, db_keys):
        """
        Test case where we add new hero references
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids).order_by("id")
        old_titles = [ref.title for ref in refs]
        assessment = refs[0].assessment
        data = {"replace": [[refs[0].id, 1010101], [refs[1].id, 1010102]]}

        serializer = ReferenceReplaceHeroIdSerializer(data=data, context={"assessment": assessment})
        assert serializer.is_valid()
        ret = serializer.execute()
        assert ret.successful()

        # ensure references changed
        refs = refs.all()
        new_titles = [ref.title for ref in refs]
        assert old_titles != new_titles

        assert new_titles == [
            "Immunoassay of haemoglobin-acrylonitrile adduct in rat as a biomarker of exposure",
            "Accumulation of environmental risks to human health: Geographical differences in the Netherlands",
        ]

    def test_valid_swap(self, db_keys):
        """
        Swap IDs on existing references.
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids).order_by("id")
        old_titles = [ref.title for ref in refs]
        assessment = refs[0].assessment
        data = {
            "replace": [
                [
                    refs[0].id,
                    int(
                        refs[1].identifiers.get(database=constants.ReferenceDatabase.HERO).unique_id
                    ),
                ],
                [
                    refs[1].id,
                    int(
                        refs[0].identifiers.get(database=constants.ReferenceDatabase.HERO).unique_id
                    ),
                ],
            ]
        }

        serializer = ReferenceReplaceHeroIdSerializer(data=data, context={"assessment": assessment})
        assert serializer.is_valid()
        ret = serializer.execute()
        assert ret.successful()

        # check new titles
        refs = refs.all()
        new_titles = [ref.title for ref in refs]
        assert old_titles != new_titles
        assert new_titles == [
            "Asbestos-induced lung injury in the sheep model: the initial alveolitis",
            "Early lung events following low-dose asbestos exposure",
        ]

    def test_duplicate(self, db_keys):
        """
        Replace would result in two references with the same HERO ID
        """
        ref_ids = [db_keys.reference_linked, db_keys.reference_unlinked]
        refs = Reference.objects.filter(id__in=ref_ids)
        assessment = refs[0].assessment
        data = {
            "replace": [
                [
                    refs[0].id,
                    refs[1].identifiers.get(database=constants.ReferenceDatabase.HERO).unique_id,
                ]
            ]
        }
        serializer = ReferenceReplaceHeroIdSerializer(data=data, context={"assessment": assessment})
        assert serializer.is_valid() is False
        assert serializer.errors["replace"][0] == "Duplicate HERO IDs in assessment: [3]"

    def test_bad_hero(self, db_keys):
        """
        Invalid HERO ID
        """
        ref = Reference.objects.get(id=db_keys.reference_linked)
        assessment = ref.assessment
        data = {"replace": [[ref.id, -1]]}
        serializer = ReferenceReplaceHeroIdSerializer(data=data, context={"assessment": assessment})
        assert serializer.is_valid() is False
        assert (
            serializer.errors["replace"][0] == "The following HERO ID(s) could not be imported: -1"
        )

    def test_bad_reference_id(self, db_keys):
        """
        Reference ID is not in assessment context
        """
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        invalid_ref = Reference.objects.filter(assessment=db_keys.assessment_final).first()
        data = {"replace": [[invalid_ref.id, 1]]}
        serializer = ReferenceReplaceHeroIdSerializer(data=data, context={"assessment": assessment})
        assert serializer.is_valid() is False
        assert serializer.errors["replace"][0] == "Reference IDs not all from assessment 1."


@pytest.mark.django_db
class TestFilterReferencesSerializer:
    def test_bad_search_id(self, db_keys):
        data = {"search_id": -1}
        expected_error = "Invalid search id"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

    def test_bad_tag_id(self, db_keys):
        data = {"tag_id": -1}
        expected_error = "Invalid tag id"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

    def test_bad_list(self, db_keys):
        data = {"required_tags": -1}
        expected_error = "Expected a comma-delimited list of ids"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"pruned_tags": -1}
        expected_error = "Expected a comma-delimited list of ids"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

    def test_bad_tag_ids(self, db_keys):
        data = {"pruned_tags": "3,-1"}
        expected_error = "Invalid tag ids"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"required_tags": "3,-1"}
        expected_error = "Invalid tag ids"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

    def test_contraints(self, db_keys):
        data = {"untagged": True, "required_tags": "1,2"}
        expected_error = "Do not combine 'untagged' with other tag filters"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"untagged": True, "pruned_tags": "1,2"}
        expected_error = "Do not combine 'untagged' with other tag filters"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"untagged": True, "tag_id": "2"}
        expected_error = "Do not combine 'untagged' with other tag filters"
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"required_tags": "2,1"}
        expected_error = (
            "'required_tags' and 'pruned_tags' require a root 'tag_id' to function correctly."
        )
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

        data = {"pruned_tags": "2,1"}
        expected_error = (
            "'required_tags' and 'pruned_tags' require a root 'tag_id' to function correctly."
        )
        with pytest.raises(exceptions.ValidationError, match=re.escape(expected_error)):
            FilterReferences.from_drf(data=data, assessment_id=db_keys.assessment_working)

    def test_success_search(self, db_keys):
        assessment_id = db_keys.assessment_conflict_resolution
        data = {
            "search_id": 7,
            "untagged": False,
            "tag_id": "33",
            "required_tags": "33",
        }
        serializer = FilterReferences.from_drf(data=data, assessment_id=assessment_id)
        assert db_keys.reference_tagged in serializer.get_queryset().values_list("id", flat=True)
