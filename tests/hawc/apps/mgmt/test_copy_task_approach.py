import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.mgmt.actions import clone_approach
from hawc.apps.mgmt.models import Task


@pytest.mark.django_db
def test_clone_approach():
    # ensure runs without failure
    dst = Assessment.objects.get(id=1)
    src = Assessment.objects.get(id=2)
    Task.objects.create_assessment_tasks(src)

    clone_approach(dst, src)

    assert len(dst.task_statuses.all()) == len(src.task_statuses.all())
    assert len(dst.task_types.all()) == len(src.task_types.all())
    assert len(dst.task_triggers.all()) == len(src.task_triggers.all())
