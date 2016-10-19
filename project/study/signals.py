from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from utils.helper import SerializerHelper

import models


def clear_cache(Model, filters):
    ids = Model.objects\
        .filter(**filters)\
        .values_list('id', flat=True)
    SerializerHelper.delete_caches(Model, ids)


@receiver(post_save, sender=models.Study)
def update_study_rob_scores(sender, instance, created, **kwargs):
    # update RiskOfBiasScores when a Study's type is changed.
    assessment = instance.get_assessment()
    for rob in instance.riskofbiases.all()\
            .select_related('study', 'study__assessment')\
            .prefetch_related('scores'):
        rob.update_scores(assessment)


@receiver(post_save, sender=models.Study)
@receiver(pre_delete, sender=models.Study)
def invalidate_caches_study(sender, instance, **kwargs):
    models.Study.delete_caches([instance.id])

    if instance.bioassay:
        clear_cache(
            apps.get_model('animal', 'Endpoint'),
            {'animal_group__experiment__study': instance.id}
        )

    if instance.epi:
        clear_cache(
            apps.get_model('epi', 'Outcome'),
            {'study_population__study': instance.id}
        )

    if instance.in_vitro:
        clear_cache(
            apps.get_model('invitro', 'ivendpoint'),
            {'experiment__study_id': instance.id}
        )

    if instance.epi_meta:
        clear_cache(
            apps.get_model('epimeta', 'MetaResult'),
            {'protocol__study': instance.id}
        )


@receiver(post_save, sender=models.Study)
def create_study_tasks(sender, instance, **kwargs):
    apps.get_model('mgmt', 'Task').objects\
        .create_study_tasks(instance)
