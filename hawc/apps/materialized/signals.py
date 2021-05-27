from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ..riskofbias.models import RiskOfBiasScore, RiskOfBiasScoreOverrideObject
from . import models


@receiver(post_save, sender=RiskOfBiasScore)
@receiver(post_delete, sender=RiskOfBiasScore)
@receiver(post_save, sender=RiskOfBiasScoreOverrideObject)
@receiver(post_delete, sender=RiskOfBiasScoreOverrideObject)
def set_score_flag(**kwargs):
    models.FinalRiskOfBiasScore.set_refresh_flag(True)
