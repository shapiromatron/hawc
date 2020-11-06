from typing import Tuple, List
import json

from django.apps import apps
from django.db import models
from django.db.models import Case, Count, IntegerField, Sum, Value, When

from ..common.models import BaseManager


class RiskOfBiasDomainManager(BaseManager):
    assessment_relation = "assessment"


class RiskOfBiasMetricManager(BaseManager):
    assessment_relation = "domain__assessment"

    def get_required_metrics(self, assessment, study):
        requireds = models.Q()
        if study.bioassay:
            requireds |= models.Q(required_animal=True)
        if study.epi or study.epi_meta:
            requireds |= models.Q(required_epi=True)
        if study.in_vitro:
            requireds |= models.Q(required_invitro=True)
        return self.get_qs(assessment).filter(requireds)

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


class RiskOfBiasManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return RiskOfBiasQuerySet(self.model, using=self._db)

    def all_active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True)

    def active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True, final=False)

    def validate_bulk_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        dst_author,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        final_only: bool,
    ):
        # all src studies from src assessment

        # all dst studies from dst assessment

        # all src metrics from src assessment

        # all dst metrics from dst assessment

        # all dst studies have no riskofbias

        # all users who authored src riskofbiases are team member
        # or higher on dst assessment

        return

    def bulk_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        dst_author,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        final_only: bool,
    ):
        self.validate_bulk_copy(
            src_assessment_id,
            dst_assessment_id,
            dst_author,
            src_dst_study_ids,
            src_dst_metric_ids,
            final_only,
        )

        Study = apps.get_model("study", "Study")
        RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")

        src_to_dst_metric_id = {src: dst for src, dst in src_dst_metric_ids}

        src_study_ids = [src_study_id for src_study_id, _ in src_dst_study_ids]
        dst_study_ids = [dst_study_id for _, dst_study_id in src_dst_study_ids]

        src_study_id_to_instance = Study.objects.in_bulk(src_study_ids)
        dst_study_id_to_instance = Study.objects.in_bulk(dst_study_ids)

        src_riskofbias_ids = []
        src_score_ids = []
        new_riskofbiases = []
        new_scores = []

        for src_study_id, dst_study_id in src_dst_study_ids:
            src_study = src_study_id_to_instance[src_study_id]
            dst_study = dst_study_id_to_instance[dst_study_id]

            riskofbiases = src_study.riskofbiases.all()
            if final_only:
                riskofbiases = riskofbiases.filter(final=True)

            for riskofbias in riskofbiases:
                for score in riskofbias.scores.all():
                    import pdb

                    pdb.set_trace()
                    if src_to_dst_metric_id.get(score.metric) is None:
                        continue
                    src_score_ids.append(score.pk)
                    score.pk = None
                    score.metric = src_to_dst_metric_id[score.metric]
                    new_scores.append(score)

                src_riskofbias_ids.append(riskofbias.pk)
                riskofbias.pk = None
                riskofbias.study = dst_study
                riskofbias.author = dst_author
                if final_only:
                    riskofbias.final = False
                    riskofbias.active = True
                new_riskofbiases.append(riskofbias)

        dst_riskofbiases = self.bulk_create(new_riskofbiases)
        dst_riskofbias_ids = [obj.pk for obj in dst_riskofbiases]
        dst_scores = RiskOfBiasScore.objects.bulk_create(new_scores)
        dst_score_ids = [obj.pk for obj in dst_scores]

        src_to_dst = dict()
        src_to_dst["study"] = {src: dst for src, dst in src_dst_study_ids}
        src_to_dst["metric"] = {src: dst for src, dst in src_dst_metric_ids}
        src_to_dst["riskofbias"] = {
            src: dst for src, dst in zip(src_riskofbias_ids, dst_riskofbias_ids)
        }
        src_to_dst["score"] = {src: dst for src, dst in zip(src_score_ids, dst_score_ids)}

        Log = apps.get_model("assessment", "Log")
        log = Log.objects.create(assessment_id=dst_assessment_id, message=json.dumps(src_to_dst),)
        return log.id


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = "riskofbias__study__assessment"


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = "assessment"
