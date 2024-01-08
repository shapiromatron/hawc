from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from .cache import UDFCache


@receiver(post_save, sender=models.ModelBinding)
def delete_cache(sender, instance, created, **kwargs):
    if not created:
        UDFCache.clear_model_binding_cache(instance)
