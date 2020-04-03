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


@pytest.mark.django_db
def test_bulk_tag_application():
    ref = Reference.objects.get(id=1)
    tags_on_ref = ref.tags.all()
    assert len(tags_on_ref) == 0

    ref_ids = [ref.id]

    # insert a few dummy references
    for i in range(0, 5):
        ref.id = None
        ref.save()
        ref_ids.append(ref.id)

    INCLUSION_TAG = 2
    HUMAN_STUDY_TAG = 3
    tag_ids = [INCLUSION_TAG, HUMAN_STUDY_TAG]

    # apply bulk-tags to all but the last study
    Reference.apply_bulk_tags(ref_ids[0:-1], tag_ids)

    # now reload the individual references and make sure they have both expected tags
    idx = 0
    for ref_id in ref_ids:
        found_inclusion = False
        found_human = False
        check_ref = Reference.objects.get(id=ref_id)
        tags = check_ref.tags.all()
        for tag in tags:
            if tag.id == INCLUSION_TAG:
                found_inclusion = True
            elif tag.id == HUMAN_STUDY_TAG:
                found_human = True

        if idx < len(ref_ids) - 1:
            # 0 -> n-1 references had the tags applied...
            assert found_inclusion is True
            assert found_human is True
        else:
            # the last reference did NOT
            assert found_inclusion is False
            assert found_human is False

        idx += 1
