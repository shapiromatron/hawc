import pytest

from hawc.apps.mgmt import constants
from hawc.apps.mgmt.models import Task
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestTaskManager:
    def test_trigger_workflow(self):
        study = Study.objects.get(assessment_id=1)
        user = HAWCUser.objects.get(email="admin@hawcproject.org")

        Task.objects.ensure_preparation_started(study, user)
        task = Task.objects.get(study=study, type__name="Preparation")
        self._assert_task_status(task, user, constants.TaskStatus.STARTED)

        Task.objects.ensure_extraction_started(study, user)
        self._assert_task_status(task, user, constants.TaskStatus.COMPLETED)
        task = Task.objects.get(study=study, type__name="Data Extraction")
        self._assert_task_status(task, user, constants.TaskStatus.STARTED)

        Task.objects.ensure_rob_started(study, user)
        task = Task.objects.get(study=study, type__name="Study Evaluation")
        self._assert_task_status(task, user, constants.TaskStatus.STARTED)

        Task.objects.ensure_rob_stopped(study)
        self._assert_task_status(task, user, constants.TaskStatus.COMPLETED)

    def _assert_task_status(self, task, user, status):
        task.refresh_from_db()
        assert task.owner == user
        assert task.status.value == status
