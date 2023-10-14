import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..common.helper import SerializerHelper
from . import models
from .tasks import run_job

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Assessment)
def default_configuration(sender, instance, created, **kwargs):
    """
    Created default assessment settings when a new assessment instance
    is created.
    """
    if created:
        logger.info("Creating default literature inclusion/exclusion tags")
        apps.get_model("lit", "ReferenceFilterTag").build_default(instance)
        apps.get_model("lit", "LiteratureAssessment").build_default(instance)
        apps.get_model("lit", "Search").build_default(instance)

        logger.info(
            f"Creating default settings for {instance.get_rob_name_display().lower()} criteria"
        )
        apps.get_model("riskofbias", "RiskOfBiasAssessment").build_default(instance)

        logger.info("Creating new BMD settings assessment creation")
        apps.get_model("bmd", "AssessmentSettings").build_default(instance)

        logger.info("Creating default summary text")
        apps.get_model("summary", "SummaryText").build_default(instance)

        logger.info("Building in-vitro endpoint category-root")
        apps.get_model("invitro", "IVEndpointCategory").create_root(assessment_id=instance.pk)

    apps.get_model("mgmt", "Task").objects.create_assessment_tasks(assessment=instance)


@receiver(post_save, sender=models.Assessment)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    SerializerHelper.clear_cache(
        apps.get_model("animal", "Endpoint"), {"assessment_id": instance.id}
    )


@receiver(pre_save, sender=models.Job)
def null_to_dict(sender, instance, **kwargs):
    """
    Turns null "kwarg" entries into an empty dict.

    Problem:
    https://stackoverflow.com/questions/55147169/django-admin-jsonfield-default-empty-dict-wont-save-in-admin
    Fix:
    Allowing blank/null and fixing them here.
    """
    if instance.kwargs is None:
        instance.kwargs = {}


@receiver(post_save, sender=models.Job)
def run_task(sender, instance, created, **kwargs):
    if created:
        run_job.apply_async(task_id=instance.task_id)
