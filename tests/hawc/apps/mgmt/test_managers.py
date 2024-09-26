import pytest

from hawc.apps.mgmt import constants
from hawc.apps.mgmt.models import Task, TaskStatus
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestTaskManager:
    def test_user_progress_update(self):
        study = Study.objects.get(assessment_id=1)
        task = Task.objects.get(study=study, owner=1, type=1, status=1)
        next_task = Task.objects.get(study=study, owner=1, type=2, status=1)

        next_status = TaskStatus.objects.get(assessment=study.assessment, order=30)
        task.status = next_status
        task.save()

        # call update method
        Task.objects.progress_next_status(task=task)
        assert task.status.order == constants.TaskStatus.COMPLETED

        next_task.refresh_from_db()
        assert next_task.status.order == constants.TaskStatus.STARTED

    def test_trigger_workflow(self):
        study = Study.objects.get(assessment_id=1)
        user = HAWCUser.objects.get(email="admin@hawcproject.org")

        # want to keep database changes between method calls
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
