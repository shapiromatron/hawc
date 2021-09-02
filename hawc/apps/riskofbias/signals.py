import logging

from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.RiskOfBiasDomain)
@receiver(pre_delete, sender=models.RiskOfBiasDomain)
@receiver(post_save, sender=models.RiskOfBiasMetric)
@receiver(pre_delete, sender=models.RiskOfBiasMetric)
def invalidate_caches_rob_metrics(sender, instance, **kwargs):
    Study = apps.get_model("study", "Study")
    if sender is models.RiskOfBiasDomain:
        assessment_id = instance.assessment_id
    elif sender is models.RiskOfBiasMetric:
        assessment_id = instance.domain.assessment_id

    ids = Study.objects.filter(assessment_id=assessment_id).values_list("id", flat=True)

    Study.delete_caches(ids)


@receiver(post_save, sender=models.RiskOfBiasMetric)
def update_study_type_metrics(sender, instance, created, **kwargs):
    # Create or delete RiskOfBiasScores when RiskOfBiasMetric are updated
    assessment = instance.get_assessment()
    robs = (
        models.RiskOfBias.objects.filter(study__assessment=assessment)
        .select_related("study", "study__assessment")
        .prefetch_related("scores")
    )
    with transaction.atomic():
        for rob in robs:
            rob.create_or_delete_scores(assessment)


@receiver(post_save, sender=models.RiskOfBias)
@receiver(pre_delete, sender=models.RiskOfBias)
@receiver(post_save, sender=models.RiskOfBiasScore)
@receiver(pre_delete, sender=models.RiskOfBiasScore)
def invalidate_caches_risk_of_bias(sender, instance, **kwargs):
    Study = apps.get_model("study", "Study")
    if sender is models.RiskOfBias:
        rob_ids = [instance.id]
        study_ids = [instance.study_id]
    elif sender is models.RiskOfBiasScore:
        rob_ids = [instance.riskofbias.id]
        study_ids = [instance.riskofbias.study_id]

    models.RiskOfBias.delete_caches(rob_ids)
    Study.delete_caches(study_ids)
