from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.apps import apps

import models


@receiver(post_save, sender=models.Reference)
@receiver(pre_delete, sender=models.Reference)
def invalidate_study_cache(sender, instance, **kwargs):
    Study = apps.get_model('study', 'Study')
    Study.delete_caches([instance.id])


@receiver(post_save, sender=models.ReferenceFilterTag)
@receiver(pre_delete, sender=models.ReferenceFilterTag)
def invalidate_tag_cache(sender, instance, **kwargs):
    try:
        # may be root-node
        assessment_id = instance.get_assessment_id()
        instance.clear_cache(assessment_id)
    except IndexError:
        pass
