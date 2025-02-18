import pytest

from hawc.apps.common.signals import ignore_signals
from hawc.apps.mgmt.models import Task, TaskType


@pytest.mark.django_db
class TestTaskTypeSignal:
    def test_signal(self):
        # setup
        with ignore_signals():
            type = TaskType.objects.create(
                assessment_id=2,
                name="test",
                order=10,
            )
            qs = Task.objects.filter(type=type)

            type.name = "Preparation"
            type.save()
            assert qs.count() == 0

        # with signal, we create new tasks when a task type is added
        type.name = "test"
        type.save()
        assert qs.count() == 4
