import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, Count, IntegerField, QuerySet, Sum, Value, When

from ..common.models import BaseManager, pd_strip_tags, sql_display
from ..study.managers import study_df_annotations, study_df_mapping
from . import constants


class RiskOfBiasDomainManager(BaseManager):
    assessment_relation = "assessment"


class RiskOfBiasMetricManager(BaseManager):
    assessment_relation = "domain__assessment"

    def get_required_metrics(self, study):
        filters = models.Q()
        if study.bioassay:
            filters |= models.Q(required_animal=True)
        if study.epi or study.epi_meta:
            filters |= models.Q(required_epi=True)
        if study.in_vitro:
            filters |= models.Q(required_invitro=True)
        if not filters:
            return self.get_qs(study.assessment_id).none()
        return self.get_qs(study.assessment_id).filter(filters)

    def get_metrics_for_visuals(self, assessment_id):
        return self.get_qs(assessment_id).values("id", "name")


class RiskOfBiasQuerySet(models.QuerySet):
    def num_scores(self):
        return self.annotate(num_scores=Count("scores"))

    def num_override_scores(self):
        return self.annotate(
            num_override_scores=Sum(
                Case(
                    When(scores__is_default=False, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
        )

    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self


class RiskOfBiasScoreOverrideObjectQuerySet(models.QuerySet):
    def _get_orphan_ids(self) -> list[int]:
        """
        Return object IDs where the content-object no longer exists
        """
        cts = self.values_list("content_type", flat=True).distinct()
        deletions: list[int] = []
        for ct in cts:
            all_ids = self.filter(content_type=ct).values_list("object_id", flat=True)
            RelatedClass = ContentType.objects.get_for_id(ct).model_class()
            matched_ids = RelatedClass.objects.filter(id__in=all_ids).values_list("id", flat=True)
            deleted_ids = list(set(all_ids) - set(matched_ids))
            if deleted_ids:
                override_ids = self.filter(content_type=ct, object_id__in=deleted_ids).values_list(
                    "id", flat=True
                )
                deletions.extend(list(override_ids))
        return deletions

    def orphaned(self):
        return self.filter(id__in=self._get_orphan_ids())

    def not_orphaned(self):
        return self.exclude(id__in=self._get_orphan_ids())


class RiskOfBiasManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return RiskOfBiasQuerySet(self.model, using=self._db)

    def get_required_robs_for_metric(self, metric):
        assessment = metric.get_assessment()
        filters = models.Q()
        if metric.required_animal:
            filters |= models.Q(study__bioassay=True)
        if metric.required_epi:
            filters |= models.Q(study__epi=True)
            filters |= models.Q(study__epi_meta=True)
        if metric.required_invitro:
            filters |= models.Q(study__in_vitro=True)
        if not filters:
            return self.get_qs(assessment.id).none()
        return self.get_qs(assessment.id).filter(filters)


class RiskOfBiasScoreQuerySet(QuerySet):
    def df(self) -> pd.DataFrame:
        mapping = {
            # study
            **study_df_mapping("study-", "riskofbias__study__"),
            # rob
            "rob-id": "riskofbias_id",
            "rob-created": "riskofbias__created",
            "rob-last_updated": "riskofbias__last_updated",
            # domain
            "rob-domain_id": "metric__domain_id",
            "rob-domain_name": "metric__domain__name",
            "rob-domain_description": "metric__description",
            # metric
            "rob-metric_id": "metric_id",
            "rob-metric_name": "metric__name",
            "rob-metric_description": "metric__description",
            # score
            "rob-score_id": "id",
            "rob-score_is_default": "is_default",
            "rob-score_label": "label",
            "rob-score": "score",
            "rob-score_display": Value("-"),
            "rob-score_symbol": Value("-"),
            "rob-score_shade": Value("-"),
            "rob-score_bias_direction": "bias_direction",
            "rob-score_bias_direction_display": sql_display(
                "bias_direction", constants.BiasDirections
            ),
            "rob-score_notes": "notes",
        }
        qs = (
            self.annotate(**study_df_annotations("riskofbias__study__"))
            .values_list(*list(mapping.values()))
            .order_by("riskofbias__study__id", "metric_id", "id")
        )
        df = pd.DataFrame(data=qs, columns=list(mapping.keys()))
        df.loc[:, "rob-score_display"] = df["rob-score"].map(constants.SCORE_CHOICES_MAP)
        df.loc[:, "rob-score_symbol"] = df["rob-score"].map(constants.SCORE_SYMBOLS)
        df.loc[:, "rob-score_shade"] = df["rob-score"].map(constants.SCORE_SHADES)
        pd_strip_tags(
            df,
            [
                "study-summary",
                "rob-domain_description",
                "rob-metric_description",
                "rob-score_notes",
            ],
        )
        return df


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = "riskofbias__study__assessment"

    def get_queryset(self):
        return RiskOfBiasScoreQuerySet(self.model, using=self._db)


class RiskOfBiasScoreOverrideObjectManager(BaseManager):
    def get_queryset(self):
        return RiskOfBiasScoreOverrideObjectQuerySet(self.model, using=self._db)


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = "assessment"
