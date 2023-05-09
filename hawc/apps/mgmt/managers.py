import logging

from django.db.models import QuerySet

from ..common.models import BaseManager
from ..study.models import Study
from . import constants

logger = logging.getLogger(__name__)


class TaskQuerySet(QuerySet):
    def owned_by(self, user):
        return self.filter(owner=user)

    def exclude_completed_and_abandonded(self):
        return self.exclude(
            status__in=[constants.TaskStatus.COMPLETED, constants.TaskStatus.ABANDONED]
        )


class TaskManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

    def create_assessment_tasks(self, assessment):
        """
        Create tasks for all studies in assessment and save to database.

        Tasks are only added, not removed with changes. Method called via
        signal whenever assessment is created/modified.
        """
        if not assessment.enable_project_management:
            return
        studies = Study.objects.assessment_qs(assessment.id).prefetch_related("tasks")
        tasks = []
        for study in studies:
            tasks.extend(self._get_missing_tasks(study, assessment))
        logger.info(f"Creating {len(tasks)} tasks for assessment {assessment.id}.")
        self.bulk_create(tasks)

    def create_study_tasks(self, study):
        """
        Create tasks for study and save to database.

        Method called via signal whenever a study is created/modified.
        """
        assessment = study.assessment
        if not assessment.enable_project_management:
            return
        tasks = self._get_missing_tasks(study, assessment)
        logger.info(f"Creating {len(tasks)} tasks for study {study.id}.")
        self.bulk_create(tasks)

    def _get_missing_tasks(self, study, assessment):
        """Return list of unsaved Task objects for single study."""
        existing_tasks = study.tasks.all()
        new_tasks = []

        def task_by_type(qs, task_type):
            """Get task if exists in qs, else return None."""
            for task in qs:
                if task.type == task_type:
                    return task
            return None

        # create prep task
        task = task_by_type(existing_tasks, constants.TaskType.PREPARATION)
        if task is None:
            new_tasks.append(self.model(study=study, type=constants.TaskType.PREPARATION))

        # create extraction tasks
        if assessment.enable_data_extraction:
            task = task_by_type(existing_tasks, constants.TaskType.EXTRACTION)
            if task is None:
                new_tasks.append(self.model(study=study, type=constants.TaskType.EXTRACTION))

            task = task_by_type(existing_tasks, constants.TaskType.QA)
            if task is None:
                new_tasks.append(self.model(study=study, type=constants.TaskType.QA))

        # create rob tasks
        if assessment.enable_risk_of_bias:
            task = task_by_type(existing_tasks, constants.TaskType.ROB)
            if task is None:
                new_tasks.append(self.model(study=study, type=constants.TaskType.ROB))

        return new_tasks

    def ensure_preparation_started(self, study, user):
        """Start preparation task if not started."""
        task = self.filter(study=study, type=constants.TaskType.PREPARATION).first()
        if task:
            task.start_if_unstarted(user)

    def ensure_preparation_stopped(self, study):
        """Stop preparation task if started."""
        task = self.filter(study=study, type=constants.TaskType.PREPARATION).first()
        if task:
            task.stop_if_started()

    def ensure_extraction_started(self, study, user):
        """Start extraction task if not started."""
        task = self.filter(study=study, type=constants.TaskType.EXTRACTION).first()
        if task:
            task.start_if_unstarted(user)

    def ensure_rob_started(self, study, user):
        """Start RoB task if not started."""
        task = self.filter(study=study, type=constants.TaskType.ROB).first()
        if task:
            task.start_if_unstarted(user)

    def ensure_rob_stopped(self, study):
        """Stop RoB task if started."""
        task = self.filter(study=study, type=constants.TaskType.ROB).first()
        if task:
            task.stop_if_started()
