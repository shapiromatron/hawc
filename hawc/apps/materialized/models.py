import json

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import connection, models

from ..riskofbias.constants import NA_SCORES, SCORE_CHOICES_MAP
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
    def create(cls):
        with connection.cursor() as cursor:
            cursor.execute(cls.sql.create)

    @classmethod
    def drop(cls):
        with connection.cursor() as cursor:
            cursor.execute(cls.sql.drop)

    @classmethod
    def set_refresh_flag(cls, refresh: bool):
        cache.set(f"refresh-{cls._meta.db_table}", refresh)

    @classmethod
    def should_refresh(cls) -> bool:
        return bool(cache.get(f"refresh-{cls._meta.db_table}", False))

    @classmethod
    def refresh(cls, force: bool = False):
        if force or cls.should_refresh():
            with connection.cursor() as cursor:
                cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cls._meta.db_table}")
            cls.set_refresh_flag(False)


class FinalRiskOfBiasScore(MaterializedViewModel):
    sql = sql.FinalRiskOfBiasScore

    objects = managers.FinalRiskOfBiasScoreManager()

    score = models.ForeignKey(
        "riskofbias.RiskOfBiasScore",
        on_delete=models.DO_NOTHING,
        related_name="final_scores",
    )
    score_label = models.CharField(max_length=128)
    score_notes = models.TextField()
    score_score = models.PositiveSmallIntegerField(verbose_name="Score")
    bias_direction = models.PositiveSmallIntegerField()
    is_default = models.BooleanField()

    metric = models.ForeignKey(
        "riskofbias.RiskOfBiasMetric",
        on_delete=models.DO_NOTHING,
        related_name="final_scores",
    )
    riskofbias = models.ForeignKey(
        "riskofbias.RiskOfBias", on_delete=models.DO_NOTHING, related_name="final_scores"
    )
    study = models.ForeignKey(
        "study.Study", on_delete=models.DO_NOTHING, related_name="final_scores"
    )

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.IntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def get_dp_export(cls, assessment_id: int, ids: list[int], data_type: str) -> tuple[dict, dict]:
        """
        Given an assessment, a list of object ids, and a data type, return all the data required to
        build a data pivot risk of bias export for only active, final data.

        Args:
            assessment_id (int): An assessment identifier
            ids (list[int]): A list of object ids to include, dependent on data_type:
                "animal" takes endpoint ids
                "epi" takes outcome ids
                "invitro" takes study ids
            data_type (str): The data type to use; one of {"animal", "epi", "invitro"}

        Returns:
            tuple[dict, dict]: A {metric_id: header_name} dict for building headers, and a
                {(object_id, metric_id): text} dict for building rows
        """

        data_types = {"animal", "epi", "invitro"}
        if data_type not in data_types:
            raise ValueError(f"Unsupported data type {data_type}; expected {data_types}")

        filters = dict(domain__assessment_id=assessment_id)
        qs = cls.objects.filter(study__assessment_id=assessment_id)
        if data_type == "animal":
            filters["required_animal"] = True
            scores_map = qs.endpoint_scores(ids)
        elif data_type == "epi":
            filters["required_epi"] = True
            scores_map = qs.outcome_scores(ids)
        elif data_type == "invitro":
            filters["required_invitro"] = True
            scores_map = qs.study_scores(ids)

        # return headers
        RiskOfBiasMetric = apps.get_model("riskofbias", "RiskOfBiasMetric")
        metric_qs = list(
            RiskOfBiasMetric.objects.filter(**filters).select_related("domain").order_by("id")
        )
        header_map = {metric.id: "" for metric in metric_qs}
        for metric in metric_qs:
            if metric.domain.is_overall_confidence:
                text = "Overall study confidence"
            elif metric.use_short_name:
                text = f"RoB ({metric.short_name})"
            else:
                text = f"RoB ({metric.domain.name}: {metric.name})"
            header_map[metric.id] = text

        # return data
        metric_ids = list(header_map.keys())
        default_value = '{"sortValue": -1, "display": "N/A"}'

        for metric_id in metric_ids:
            for id in ids:
                key = (id, metric_id)
                if key in scores_map:
                    # convert values in our map to a str-based JSON
                    score = scores_map[key]["score_score"]
                    content = json.dumps({"sortValue": score, "display": SCORE_CHOICES_MAP[score]})

                    # special case for N/A
                    if score in NA_SCORES:
                        content = default_value

                    scores_map[key] = content

                else:
                    scores_map[key] = default_value

        return header_map, scores_map
