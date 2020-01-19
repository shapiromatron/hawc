import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.SelectedModel)
@receiver(pre_delete, sender=models.SelectedModel)
def invalidate_outcome_cache(sender, instance, **kwargs):
    logging.info("Clearing endpoint cache: {}".format(instance.endpoint_id))
    apps.get_model("animal", "Endpoint").delete_caches([instance.endpoint_id])
