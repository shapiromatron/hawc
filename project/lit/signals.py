from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.apps import apps

from . import models


@receiver(post_save, sender=models.Reference)
@receiver(pre_delete, sender=models.Reference)
def invalidate_study_cache(sender, instance, **kwargs):
    Study = apps.get_model('study', 'Study')
    Study.delete_caches([instance.id])
