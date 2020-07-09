import pytest
from rest_framework.exceptions import ValidationError

from hawc.apps.common.serializers import get_matching_instance, get_matching_instances
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
