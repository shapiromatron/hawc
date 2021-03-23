from django.apps import apps
from django.core.cache import cache
from django.db import connection, models, transaction

from . import managers


class MaterializedView(models.Model):
    class Meta:
        abstract = True
        managed = False

    @classmethod
    def set_refresh_cache(cls, bool):
        cache.set(f"refresh-{cls._meta.db_table}", bool)

    @classmethod
    def get_refresh_cache(cls):
        cache.get(f"refresh-{cls._meta.db_table}", False)

    @classmethod
    @transaction.atomic
    def refresh_view(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cls._meta.db_table}")


class Score(MaterializedView):
    objects = managers.MaterializedScoreManager

    score = models.ForeignKey(
        "riskofbias.RiskOfBiasScore",
        on_delete=models.DO_NOTHING,
        related_name="materialized_scores",
    )
    score_score = models.SmallIntegerField()
    is_default = models.BooleanField()

    metric = models.ForeignKey(
        "riskofbias.RiskOfBiasMetric",
        on_delete=models.DO_NOTHING,
        related_name="materialized_scores",
    )
    riskofbias = models.ForeignKey(
        "riskofbias.RiskOfBias", on_delete=models.DO_NOTHING, related_name="materialized_scores"
    )
    study = models.ForeignKey(
        "study.Study", on_delete=models.DO_NOTHING, related_name="materialized_scores"
    )

    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    object_id = models.IntegerField()

    def get_override_class(self):
        return apps.get_model(self.app_label, self.model)

    def get_override_object(self):
        return self.get_override_class().objects.get(pk=self.object_id)
