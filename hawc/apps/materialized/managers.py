from django.db import models


class FinalRiskOfBiasScoreQuerySet(models.QuerySet):
    def prioritized_scores(self):
        # return endpoint overrides
        qs = self.filter(app_label="animal", model="endpoint")
        if qs.exists():
            return qs
        # return animal group overrides
        qs = self.filter(app_label="animal", model="animalgroup")
        if qs.exists():
            return qs
        # return default scores
        return self.filter(is_default=True)


class FinalRiskOfBiasScoreManager(models.Manager):
    def get_queryset(self):
        return FinalRiskOfBiasScoreQuerySet(self.model, using=self._db)
