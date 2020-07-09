import pytest
from rest_framework.exceptions import ValidationError

from hawc.apps.common.serializers import get_matching_instance
from hawc.apps.study.models import Study


@pytest.mark.django_db
def test_user_can_edit_object(db_keys):
    working = Study.objects.get(id=db_keys.study_working)

    # success
    assert working == get_matching_instance(Study, {"study_id": db_keys.study_working}, "study_id")

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
