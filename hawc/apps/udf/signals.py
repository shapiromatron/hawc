from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models
from .cache import UDFCache


@receiver(post_save, sender=models.ModelBinding)
@receiver(pre_delete, sender=models.ModelBinding)
def delete_cache(sender, instance, **kwargs):
    UDFCache.clear_model_binding_cache(instance)
