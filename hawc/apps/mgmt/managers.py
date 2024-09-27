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
        return self.exclude(status__terminal_status=True)


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
        statuses = []
        types = assessment.task_types.all()

        # get default assessment setup if not created
        if not types:
            statuses = self._get_missing_statuses(assessment)
            types = self._get_missing_types(assessment)

        for study in studies:
            if types:
                # add tasks according to new task types
                tasks.extend(self._get_updated_tasks(study))
            else:
                # create default tasks
                tasks.extend(self._get_missing_tasks(study, statuses, types))

        logger.info(f"Creating {len(tasks)} tasks for assessment {assessment.id}.")
        self.bulk_create(tasks)

        # load initial default triggers
        if not assessment.task_triggers.all():
            self._create_default_assessment_triggers(assessment, statuses, types)

    def create_study_tasks(self, study):
        """
        Create tasks for study and save to database.

        Method called via signal whenever a study is created/modified.
        """
        assessment = study.assessment
        if not assessment.enable_project_management:
            return

        # Create default tasks only if a new study is created
        if study.tasks.all():
            tasks = self._get_updated_tasks(study)
        else:
            statuses = study.assessment.task_statuses.all()
            types = study.assessment.task_types.all()
            tasks = self._get_missing_tasks(study, statuses, types)

        logger.info(f"Creating {len(tasks)} tasks for study {study.id}.")
        self.bulk_create(tasks)

    def progress_next_status(self, task):
        """
        If a user assigned task is set to a terminal status, start their next task

        Method called via signal whenever a task is created/modified.
        """
        status = task.status
        type = task.type
        assessment = task.study.assessment

        if not status.terminal_status:
            return

        next_task = self.model.objects.filter(
            owner=task.owner,
            study=task.study,
            type__order__gt=type.order,
            status__terminal_status=False,
        ).first()

        # Start the next task
        if next_task:
            next_status = (
                assessment.task_statuses.filter(order__gt=next_task.status.order)
                .order_by("order")
                .exclude(terminal_status=True)
                .first()
            )

            if next_status:
                next_task.status = next_status
                next_task.save()

    def _create_default_assessment_triggers(self, assessment, statuses, types):
        """
        Create task triggers for an assessment and save to database. This
        should eventually take user-defined input, but currently creates all
        possible defined triggers for managed assessments

        Method called via signal whenever assessment is created/modified.
        """

        TaskTrigger = apps.get_model("mgmt", "TaskTrigger")
        triggers = []

        def create_trigger(task_type, event, trigger_type):
            """Create trigger given event and task type"""
            if trigger_type == 1:
                curr_status = self._get_task_status(constants.TaskStatus.NOT_STARTED, statuses)
                next_status = self._get_task_status(constants.TaskStatus.STARTED, statuses)
            elif trigger_type == 2:
                curr_status = self._get_task_status(constants.TaskStatus.STARTED, statuses)
                next_status = self._get_task_status(constants.TaskStatus.COMPLETED, statuses)

            if curr_status and next_status:
                triggers.append(
                    TaskTrigger(
                        assessment=assessment,
                        task_type=task_type,
                        current_status=curr_status,
                        next_status=next_status,
                        event=event,
                    )
                )

        # default hardcoded triggers
        for event, _ in constants.StartTaskTriggerEvent.choices:
            # for each study trigger, get the associated task types from the assessment level
            if event == constants.StartTaskTriggerEvent.STUDY_CREATION:
                task_type = self._get_task_type(constants.TaskType.PREPARATION, types)
                create_trigger(task_type, event, 1)

            elif event == constants.StartTaskTriggerEvent.DATA_EXTRACTION:
                task_type = self._get_task_type(constants.TaskType.PREPARATION, types)
                create_trigger(task_type, event, 2)
                task_type = self._get_task_type(constants.TaskType.EXTRACTION, types)
                create_trigger(task_type, event, 1)

            elif event == constants.StartTaskTriggerEvent.MODIFY_ROB:
                task_type = self._get_task_type(constants.TaskType.ROB, types)
                create_trigger(task_type, event, 1)

            elif event == constants.StartTaskTriggerEvent.COMPLETE_ROB:
                task_type = self._get_task_type(constants.TaskType.ROB, types)
                create_trigger(task_type, event, 2)

        TaskTrigger.objects.bulk_create(triggers)
        logger.info(f"Creating {len(triggers)} tasks for assessment {assessment.id}.")

    def _get_updated_tasks(self, study):
        types = self.model.objects.all()
        types = study.assessment.task_types.all()
        status = study.assessment.task_statuses.order_by("order").first()
        tasks = []
        # create new tasks set to the initial status
        for type in types:
            if not study.tasks.filter(type=type):
                new_type = self.model(study=study, type=type, status=status)
                tasks.append(new_type)
        return tasks

    def _get_missing_tasks(self, study, statuses, types):
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
            status = self._get_task_status(constants.TaskStatus.NOT_STARTED, statuses)

            if task is not None:
                continue

            if type == constants.TaskType.PREPARATION:
                new_tasks.append(
                    self.model(study=study, type=self._get_task_type(type, types), status=status)
                )

            if study.assessment.enable_data_extraction:
                if type == constants.TaskType.EXTRACTION or type == constants.TaskType.QA:
                    new_tasks.append(
                        self.model(
                            study=study, type=self._get_task_type(type, types), status=status
                        )
                    )

            if study.assessment.enable_risk_of_bias and type == constants.TaskType.ROB:
                new_tasks.append(
                    self.model(study=study, type=self._get_task_type(type, types), status=status)
                )

        return new_tasks

    def _get_missing_statuses(self, assessment):
        """Return list of all task status objects for single assessment."""
        TaskStatus = apps.get_model("mgmt", "TaskStatus")
        statuses = []
        # create all possible statuses for each task
        for value, name in constants.TaskStatus.choices:
            status_instance = TaskStatus(
                assessment=assessment,
                name=name,
                value=value,
                order=value,
                color=constants.TaskStatus.status_colors(value),
                terminal_status=self._get_terminal_status(value),
            )
            statuses.append(status_instance)
        TaskStatus.objects.bulk_create(statuses)
        return statuses

    def _get_missing_types(self, assessment):
        """Return list of all task type objects for single assessment."""
        TaskType = apps.get_model("mgmt", "TaskType")
        types = []

        for type, type_name in constants.TaskType.choices:
            type_instance = TaskType(
                assessment=assessment,
                name=type_name,
                order=type,
            )
            types.append(type_instance)

        TaskType.objects.bulk_create(types)
        return types

    def _get_task_type(self, task_type, type_list):
        """Get task by type if exists in qs, else return None."""
        for type in type_list:
            if type.order == task_type:
                return type
        return None

    def _get_task_status(self, task_status, status_list):
        """Get task status if exists in qs, else return None."""
        for status in status_list:
            if status.order == task_status:
                return status
        return None

    def _get_terminal_status(self, status):
        if status in (constants.TaskStatus.COMPLETED, constants.TaskStatus.ABANDONED):
            return True
        return False

    def ensure_preparation_started(self, study, user):
        """Start preparation task if not started."""
        tasks = self.filter(study=study)
        if tasks:
            self.trigger_changes(tasks, constants.StartTaskTriggerEvent.STUDY_CREATION, user)

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
                # get next status from the trigger
                task.status = trigger.first().next_status
                if task.started:
                    task.stop_if_started()
                else:
                    task.start_if_unstarted(user)
