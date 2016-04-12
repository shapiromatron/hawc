from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import models


@receiver(post_save, sender=models.RiskOfBiasDomain)
@receiver(pre_delete, sender=models.RiskOfBiasDomain)
@receiver(post_save, sender=models.RiskOfBiasMetric)
@receiver(pre_delete, sender=models.RiskOfBiasMetric)
def invalidate_caches_sq_metrics(sender, instance, **kwargs):
    if sender is models.RiskOfBiasDomain:
        assessment_id = instance.assessment_id
    elif sender is models.RiskOfBiasMetric:
        assessment_id = instance.domain.assessment_id

    ids = models.Study.objects\
        .filter(assessment_id=assessment_id)\
        .values_list('id', flat=True)

    models.Study.delete_caches(ids)


@receiver(post_save, sender=models.RiskOfBias)
@receiver(pre_delete, sender=models.RiskOfBias)
def invalidate_caches_study_quality(sender, instance, **kwargs):
    instance.study.delete_caches([instance.study_id])
