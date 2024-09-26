import logging

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.TaskType)
def default_configuration(sender, instance, created, **kwargs):
    """
    Update study management tasks when a new task type is added
    """
    logger.info("Updating assessment tasks")
    apps.get_model("mgmt", "Task").objects.create_assessment_tasks(assessment=instance.assessment)
