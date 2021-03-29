from django.db import models


class FinalRiskOfBiasScoreQuerySet(models.QuerySet):
    pass


class FinalRiskOfBiasScoreManager(models.Manager):
    def get_queryset(self):
        return FinalRiskOfBiasScoreQuerySet(self.model, using=self._db)
