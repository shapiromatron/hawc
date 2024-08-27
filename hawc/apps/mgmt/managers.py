import logging

from django.apps import apps
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

        # get all statuses and types
        statuses = self._get_missing_statuses(assessment)
        types = self._get_missing_types(assessment)

        for study in studies:
            tasks.extend(self._get_missing_tasks(study, assessment, statuses, types))
        logger.info(f"Creating {len(tasks)} tasks for assessment {assessment.id}.")
        self.bulk_create(tasks)

        self._create_assessment_triggers(assessment, statuses, types)

    def create_study_tasks(self, study):
        """
        Create tasks for study and save to database.

        Method called via signal whenever a study is created/modified.
        """
        assessment = study.assessment
        if not assessment.enable_project_management:
            return

        statuses = self._get_missing_statuses(assessment)
        types = self._get_missing_types(assessment)
        tasks = self._get_missing_tasks(study, assessment, statuses, types)

        logger.info(f"Creating {len(tasks)} tasks for study {study.id}.")
        self.bulk_create(tasks)

    def _create_assessment_triggers(self, assessment, task_statuses, task_types):
        """
        Create task triggers for an assessment and save to database. This
        should eventually take user-defined input, but currently creates all
        possible defined triggers for managed assessments

        Method called via signal whenever assessment is created/modified.
        """

        TaskTrigger = apps.get_model("mgmt", "TaskTrigger")

        def status_by_value(statuses, val):
            for status in statuses:
                if status.value == val:
                    return status
            return None

        def get_task_type(qs, assessment, task_type):
            """Get task if exists in qs, else return None."""
            for type in qs:
                if type.order == task_type and type.assessment == assessment:
                    return type
            return None

        # default hardcoded triggers, will clean up when using user-defined triggers
        for value, name in constants.StartTaskTriggerEvent.choices:
            task_type = None

            curr_status, next_status = (
                constants.TaskStatus.NOT_STARTED,
                constants.TaskStatus.STARTED,
            )

            # for each study trigger, get the associated task types and statuses from the assessment level
            if value == constants.StartTaskTriggerEvent.STUDY_CREATION:
                task_type = get_task_type(task_types, assessment, constants.TaskType.PREPARATION)

            elif value == constants.StartTaskTriggerEvent.DATA_EXTRACTION:
                # this event has two
                task_type = get_task_type(task_types, assessment, constants.TaskType.PREPARATION)
                curr_status = status_by_value(task_statuses, curr_status)
                next_status = status_by_value(task_statuses, next_status)

                TaskTrigger.objects.get_or_create(
                    assessment=assessment,
                    task_type=task_type,
                    current_status=curr_status,
                    next_status=next_status,
                    event=value,
                )

                task_type = get_task_type(task_types, assessment, constants.TaskType.EXTRACTION)
                curr_status, next_status = (
                    constants.TaskStatus.STARTED,
                    constants.TaskStatus.COMPLETED,
                )

            elif value == constants.StartTaskTriggerEvent.MODIFY_ROB:
                task_type = get_task_type(task_types, assessment, constants.TaskType.ROB)

            elif value == constants.StartTaskTriggerEvent.COMPLETE_ROB:
                task_type = get_task_type(task_types, assessment, constants.TaskType.ROB)
                curr_status, next_status = (
                    constants.TaskStatus.STARTED,
                    constants.TaskStatus.COMPLETED,
                )

            curr_status = status_by_value(task_statuses, curr_status)
            next_status = status_by_value(task_statuses, next_status)

            # create a trigger associated with the study assessment, task types, and statuses
            TaskTrigger.objects.get_or_create(
                assessment=assessment,
                task_type=task_type,
                current_status=curr_status,
                next_status=next_status,
                event=value,
            )

    def _get_missing_tasks(self, study, assessment, statuses, types):
        """Return list of unsaved Task objects for single study."""
        existing_tasks = study.tasks.all()
        new_tasks = []

        def task_by_type(qs, task_type):
            """Get task if exists in qs, else return None."""
            for task in qs:
                if task.type.order == task_type:
                    return task
            return None

        # create all tasks
        for type in constants.TaskType:
            task = task_by_type(existing_tasks, type)

            if task is not None:
                continue

            if type == constants.TaskType.PREPARATION:
                new_tasks.append(self.model(study=study, type=types[0], status=statuses[0]))

            if assessment.enable_data_extraction:
                if type == constants.TaskType.EXTRACTION:
                    new_tasks.append(self.model(study=study, type=types[1], status=statuses[0]))
                if type == constants.TaskType.QA:
                    new_tasks.append(self.model(study=study, type=types[2], status=statuses[0]))

            if assessment.enable_risk_of_bias and type == constants.TaskType.ROB:
                new_tasks.append(self.model(study=study, type=types[3], status=statuses[0]))

        return new_tasks

    def _get_missing_statuses(self, assessment):
        """Return list of all task status objects for single assessment."""
        TaskStatus = apps.get_model("mgmt", "TaskStatus")
        statuses = []
        # create all possible statuses for each task
        for value, name in constants.TaskStatus.choices:
            status_instance, created = TaskStatus.objects.get_or_create(
                assessment=assessment,
                name=name,
                value=value,
                order=value,
                color=self._get_status_color(value),
                terminal_status=self._get_terminal(name),
            )
            statuses.append(status_instance)
        return statuses

    def _get_missing_types(self, assessment):
        """Return list of all task type objects for single assessment."""
        TaskType = apps.get_model("mgmt", "TaskType")
        types = []

        for type, type_name in constants.TaskType.choices:
            type_instance, created = TaskType.objects.get_or_create(
                assessment=assessment,
                name=type_name,
                order=type,
            )
            types.append(type_instance)
        return types

    def _get_terminal(self, status):
        if status == "Completed" or status == "Abandoned":
            return True
        else:
            return False

    def _get_status_color(self, val):
        colors = {
            10: "#CFCFCF",
            20: "#FFCC00",
            30: "#00CC00",
            40: "#CC3333",
        }
        return colors.get(val)

    def ensure_preparation_started(self, study, user):
        """Start preparation task if not started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.STUDY_CREATION, user)

    def ensure_preparation_stopped(self, study):
        """Stop preparation task if started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.DATA_EXTRACTION)

    def ensure_extraction_started(self, study, user):
        """Start extraction task if not started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.DATA_EXTRACTION, user)

    def ensure_rob_started(self, study, user):
        """Start RoB task if not started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.MODIFY_ROB, user)

    def ensure_rob_stopped(self, study):
        """Stop RoB task if started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.COMPLETE_ROB)

    def trigger_changes(self, tasks, event, user=None):
        triggers = apps.get_model("mgmt", "TaskTrigger")

        # for each study task, check if a trigger with the same type, status, and event exists
        for task in tasks:
            trigger = triggers.objects.filter(
                event=event, task_type=task.type, current_status=task.status
            )

            if trigger.first():
                task.status = trigger.first().next_status
                task.save()

                # if a user is supplied, assign them the task
                if user:
                    task.start_if_unstarted(user)
                else:
                    task.stop_if_started()
