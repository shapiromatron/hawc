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
