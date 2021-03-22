import pytest
from rest_framework.exceptions import ValidationError

from hawc.apps.common.serializers import (
    FlexibleChoiceField,
    get_matching_instance,
    get_matching_instances,
)
from hawc.apps.study.models import Study


@pytest.mark.django_db
def test_get_matching_instance(db_keys):
    working = Study.objects.get(id=db_keys.study_working)

    # successes
    for data in [
        {"study_id": db_keys.study_working},
        {"study_id": str(db_keys.study_working)},
    ]:
        assert working == get_matching_instance(Study, data, "study_id")

    # failures
    for data in [
        {},
        {"study_id": -1},
        {"study_id": 999},
        {"study_id": None},
        {"study_id": "string"},
    ]:
        with pytest.raises(ValidationError):
            get_matching_instance(Study, data, "study_id")


@pytest.mark.django_db
def test_get_matching_instances(db_keys):
    working = Study.objects.get(id=db_keys.study_working)

    # successes
    for data in [{"study_id": [db_keys.study_working]}, {"study_id": [str(db_keys.study_working)]}]:
        assert working == get_matching_instances(Study, data, "study_id")[0]

    # failures
    for data in [
        {},
        {"study_id": None},
        {"study_id": [-1]},
        {"study_id": [999]},
        {"study_id": ["string"]},
        {"study_id": "string"},
    ]:
        with pytest.raises(ValidationError):
            get_matching_instances(Study, data, "study_id")


@pytest.mark.django_db
def test_flexible_choice_field(db_keys):
    # working = Study.objects.get(id=db_keys.study_working)
    SAMPLE_NUMERIC_CHOICES = ((0, "example"), (1, "test"))

    SAMPLE_TEXT_CHOICES = (("name", "nom de plume"), ("job", "occupation"))

    numeric_choice = FlexibleChoiceField(choices=SAMPLE_NUMERIC_CHOICES)
    text_choice = FlexibleChoiceField(choices=SAMPLE_TEXT_CHOICES)

    # either the key or a case insensitive version will resolve to the same internal value
    for valid_input in [1, "test", "TeSt"]:
        assert numeric_choice.to_internal_value(valid_input) == 1

    # works for text or numeric keys
    for valid_input in ["job", "occupation", "OcCuPaTiOn"]:
        assert text_choice.to_internal_value(valid_input) == "job"

    for invalid_input in [99, "bad input"]:
        try:
            numeric_choice.to_internal_value(invalid_input)
            assert False
        except ValidationError:
            # this is correct behavior
            pass

    # should convert raw values to readable ones
    assert numeric_choice.to_representation(0) == "example"
    assert numeric_choice.to_representation(1) == "test"

    # should throw KeyError if given a bad value to convert
    try:
        numeric_choice.to_representation(2)
        assert False
    except KeyError:
        # this is correct behavior
        pass
