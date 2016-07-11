from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from utils.helper import SerializerHelper

import models


@receiver(post_save, sender=models.Study)
@receiver(pre_delete, sender=models.Study)
def invalidate_caches_study(sender, instance, **kwargs):
    Model = None
    filters = {}

    if instance.study_type == 0:
        Model = apps.get_model('animal', 'Endpoint')
        filters["animal_group__experiment__study"] = instance.id
    elif instance.study_type == 1:
        Model = apps.get_model('epi', 'Outcome')
        filters["study_population__study"] = instance.id
    elif instance.study_type == 2:
        Model = apps.get_model('invitro', 'ivendpoint')
        filters["experiment__study_id"] = instance.id
    elif instance.study_type == 4:
        Model = apps.get_model('epimeta', 'MetaResult')
        filters["protocol__study"] = instance.id

    models.Study.delete_caches([instance.id])
    if Model:
        ids = Model.objects\
            .filter(**filters)\
            .values_list('id', flat=True)
        SerializerHelper.delete_caches(Model, ids)
