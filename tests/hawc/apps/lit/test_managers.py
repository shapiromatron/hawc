import numpy as n
import pytest

from hawc.apps.lit import models


class TestReferenceTagsManager:
    @pytest.mark.django_db
    def test_as_dataframe(self, db_keys):
        # assert empty tag list works
        df = models.ReferenceTags.objects.as_dataframe(db_keys.assessment_working)
        assert df.shape == (0, 2)
        assert df.to_csv(index=False, lineterminator="\n") == "reference_id,tag_id\n"

        # add a tag and make sure it appears
        models.Reference.objects.get(id=1).tags.set([2])
        df = models.ReferenceTags.objects.as_dataframe(db_keys.assessment_working)
        assert df.shape == (1, 2)
        assert df.to_csv(index=False, lineterminator="\n") == "reference_id,tag_id\n1,2\n"


class TestReferenceManager:
    @pytest.mark.django_db
    def test_bulk_merge_conflicts(self, db_keys):
        assessment = db_keys.assessment_conflict_resolution
        tag_ids = [34]  # Animal Study
        references_check = models.Reference.objects.filter(
            assessment=assessment, user_tags__tags__in=tag_ids, user_tags__is_resolved=False
        )
        all_assessment_refs = models.Reference.objects.filter(assessment=assessment)

        tagged_animal_before = models.Reference.objects.filter(
            assessment=assessment, tags__in=tag_ids
        ).count()

        references_before = {}
        for ref in references_check:
            references_before[ref.id] = {}
            references_before[ref.id]["tags"] = n.array(ref.tags.all().values_list("id", flat=True))
            references_before[ref.id]["users_resolved"] = n.array(
                [user_tag.is_resolved for user_tag in ref.user_tags.all()]
            )

        merge_result = all_assessment_refs.merge_tag_conflicts(
            tag_ids, db_keys.pm_user_id, False, True
        )  # preview mode enabled
        assert merge_result["message"] == "Preview mode enabled."

        # no change with preview mode
        for ref in references_check:
            tags_after = n.array(ref.tags.all().values_list("id", flat=True))
            assert n.array_equal(references_before[ref.id]["tags"], tags_after)
            resolved_after = n.array([user_tag.is_resolved for user_tag in ref.user_tags.all()])
            assert n.array_equal(references_before[ref.id]["users_resolved"], resolved_after)

        merge_result = all_assessment_refs.merge_tag_conflicts(
            tag_ids, db_keys.pm_user_id, False, False
        )  # merge mode
        assert "references updated" in merge_result["message"]

        # changes after merge mode
        for ref in references_check:
            tags_after = list(ref.tags.all().values_list("id", flat=True))
            assert not n.array_equal(references_before[ref.id]["tags"], tags_after)
            resolved_after = n.array([user_tag.is_resolved for user_tag in ref.user_tags.all()])
            assert not n.array_equal(references_before[ref.id]["users_resolved"], resolved_after)

        assert (
            models.Reference.objects.filter(assessment=assessment, tags__in=tag_ids).count()
            > tagged_animal_before
        )
