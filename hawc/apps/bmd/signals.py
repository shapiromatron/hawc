import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Session)
@receiver(pre_delete, sender=models.Session)
def invalidate_outcome_cache(sender, instance, **kwargs):
    logger.info(f"Clearing endpoint cache: {instance.endpoint_id}")
    apps.get_model("animal", "Endpoint").delete_caches([instance.endpoint_id])
