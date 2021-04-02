from typing import Tuple

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import connection, models, transaction

from . import managers, sql


def refresh_all_mvs(force: bool = False):
    mvs = apps.get_app_config("materialized").get_models()
    for mv in mvs:
        mv.refresh(force)


class MaterializedViewModel(models.Model):
    """
    Base class for materialized views.
    Django does not manage view creation automatically; that is handled by custom SQL queries in migrations.
    And since these are views, any foreign keys on these models are not "true" foreign keys, so on_delete
    should be kept as DO_NOTHING to prevent Django from enforcing foreign key constraints.
    """

    class Meta:
        abstract = True
        managed = False

    @classmethod
    def sql(cls) -> Tuple[str, str]:
        raise NotImplementedError("SQL statements must be defined on class")

    @classmethod
    def create(cls):
        with connection.cursor() as cursor:
            cursor.execute(cls.sql()[0])

    @classmethod
    def drop(cls):
        with connection.cursor() as cursor:
            cursor.execute(cls.sql()[1])

    @classmethod
    def set_refresh_flag(cls, refresh: bool):
        cache.set(f"refresh-{cls._meta.db_table}", refresh)

    @classmethod
    def should_refresh(cls):
        cache.get(f"refresh-{cls._meta.db_table}", False)

    @classmethod
    @transaction.atomic
    def _refresh(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cls._meta.db_table}")

    @classmethod
    def refresh(cls, force: bool = False):
        if force:
            cls._refresh()
        else:
            if cls.should_refresh():
                cls._refresh()
                cls.set_refresh_flag(False)


class FinalRiskOfBiasScore(MaterializedViewModel):

    objects = managers.FinalRiskOfBiasScoreManager()

    score = models.ForeignKey(
        "riskofbias.RiskOfBiasScore", on_delete=models.DO_NOTHING, related_name="final_scores",
    )
    score_score = models.SmallIntegerField(verbose_name="Score")
    is_default = models.BooleanField()

    metric = models.ForeignKey(
        "riskofbias.RiskOfBiasMetric", on_delete=models.DO_NOTHING, related_name="final_scores",
    )
    riskofbias = models.ForeignKey(
        "riskofbias.RiskOfBias", on_delete=models.DO_NOTHING, related_name="final_scores"
    )
    study = models.ForeignKey(
        "study.Study", on_delete=models.DO_NOTHING, related_name="final_scores"
    )

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def sql(cls):
        return sql.FinalRiskOfBiasScore
