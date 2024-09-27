from textwrap import dedent

from django.db import transaction

from ...assessment.models import Assessment, Log
from ..models import Task


@transaction.atomic
def clone_approach(
    dest_assessment: Assessment, src_assessment: Assessment, user_id: int | None = None
):
    """
    Clone approach from one assessment to another.
    """

    # log about changes being made
    tasks = Task.objects.filter(study__assessment=dest_assessment)
    task_types = dest_assessment.task_types.all()
    task_statuses = dest_assessment.task_statuses.all()
    task_triggers = dest_assessment.task_triggers.all()

    log_message = dedent(
        f"""\
        Cloning Task setup approach: {src_assessment.id} -> {dest_assessment.id}
        Deleting {tasks.count()} TaskType objects
        Deleting {task_types.count()} TaskType objects
        Deleting {task_statuses.count()} TaskStatus objects
        Deleting {task_triggers.count()} TaskTrigger objects
        """
    )
    Log.objects.create(assessment=dest_assessment, user_id=user_id, message=log_message)

    # delete existing data (recursively deletes task triggers, types, statueses, etc)
    tasks.delete()
    task_triggers.delete()
    task_types.delete()
    task_statuses.delete()

    # copy task setup to new assessment (new tasks should be auto-created by trigger)
    for status in src_assessment.task_statuses.all():
        status.id = None
        status.assessment = dest_assessment
        status.save()

    for type in src_assessment.task_types.all():
        type.id = None
        type.assessment = dest_assessment
        type.save()

    for trigger in src_assessment.task_triggers.all():
        trigger.id = None
        trigger.assessment = dest_assessment
        trigger.save()
