import json
from enum import IntEnum
from typing import List, Tuple

from django.apps import apps
from django.core.exceptions import ValidationError
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

    class RoBCopyMode(IntEnum):
        """Copy mode for bulk_copy"""

        ORIGINAL = 1
        FINAL_AS_INITIAL = 2

    class RoBCopyAuthor(IntEnum):
        """Author mode for bulk_copy"""

        ORIGINAL = 1
        OTHER = 2

    def validate_bulk_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        dst_author,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        copy_mode: int,
        author_mode: int,
        **kwargs,
    ):

        # extra kwargs are invalid
        if len(kwargs) > 0:
            raise ValidationError(f"Invalid argument(s) {', '.join(kwargs.keys())}")

        # copy and author modes must be valid
        try:
            copy_mode = self.RoBCopyMode(copy_mode)
        except ValueError:
            raise ValidationError(f"Invalid copy mode {copy_mode}")
        try:
            author_mode = self.RoBCopyAuthor(author_mode)
        except ValueError:
            raise ValidationError(f"Invalid author mode {author_mode}")

        # src and dst assessments are different
        if src_assessment_id == dst_assessment_id:
            raise ValidationError("Source and destination assessments must be different")

        # studies and metrics are unique
        src_study_ids = [src for src, _ in src_dst_study_ids]
        if len(src_study_ids) > len(set(src_study_ids)):
            raise ValidationError("Source study ids must be unique")
        dst_study_ids = [dst for _, dst in src_dst_study_ids]
        if len(dst_study_ids) > len(set(dst_study_ids)):
            raise ValidationError("Destination study ids must be unique")
        src_metric_ids = [src for src, _ in src_dst_metric_ids]
        if len(src_metric_ids) > len(set(src_metric_ids)):
            raise ValidationError("Source metric ids must be unique")
        dst_metric_ids = [dst for _, dst in src_dst_metric_ids]
        if len(dst_metric_ids) > len(set(dst_metric_ids)):
            raise ValidationError("Destination metric ids must be unique")

        # all src studies from src assessment
        Study = apps.get_model("study", "Study")
        src_studies = Study.objects.filter(pk__in=src_study_ids, assessment_id=src_assessment_id)
        invalid_src_study_ids = set(src_study_ids) - set(src_studies.values_list("pk", flat=True))
        if len(invalid_src_study_ids) > 0:
            raise ValidationError(
                f"Invalid source study(ies) {', '.join([str(id) for id in invalid_src_study_ids])}; not found in assessment {src_assessment_id}"
            )

        # all dst studies from dst assessment
        dst_studies = Study.objects.filter(pk__in=dst_study_ids, assessment_id=dst_assessment_id)
        invalid_dst_study_ids = set(dst_study_ids) - set(dst_studies.values_list("pk", flat=True))
        if len(invalid_dst_study_ids) > 0:
            raise ValidationError(
                f"Invalid destination study(ies) {', '.join([str(id) for id in invalid_dst_study_ids])}; not found in assessment {dst_assessment_id}"
            )

        # all dst studies have no riskofbias
        dst_riskofbiases = self.filter(study__in=dst_study_ids)
        if dst_riskofbiases.exists():
            raise ValidationError(f"Risk of bias data already exists in destination study(ies)")

        # all src metrics from src studies should be given
        RiskOfBiasMetric = apps.get_model("riskofbias", "RiskOfBiasMetric")
        src_metrics = RiskOfBiasMetric.objects.filter(
            pk__in=src_metric_ids, domain__assessment_id=src_assessment_id
        )
        invalid_src_metric_ids = set(src_metric_ids) - set(src_metrics.values_list("pk", flat=True))

        if len(invalid_src_metric_ids) > 0:
            raise ValidationError(
                f"Invalid source metric(s) {', '.join([str(id) for id in invalid_src_metric_ids])}"
            )
        missing_src_metrics = RiskOfBiasMetric.objects.filter(
            domain__assessment_id=src_assessment_id
        ).exclude(pk__in=src_metric_ids)
        if missing_src_metrics.exists():
            raise ValidationError(
                f"Need mapping for source metric(s) {', '.join([str(metric.pk) for metric in missing_src_metrics])}"
            )

        # all dst metrics from dst assessment
        dst_metrics = RiskOfBiasMetric.objects.filter(
            pk__in=dst_metric_ids, domain__assessment_id=dst_assessment_id
        )
        invalid_dst_metric_ids = set(dst_metric_ids) - set(dst_metrics.values_list("pk", flat=True))

        if len(invalid_dst_metric_ids) > 0:
            raise ValidationError(
                f"Invalid destination metric(s) {', '.join([str(id) for id in invalid_dst_metric_ids])}"
            )

        # all users who authored src riskofbiases are team member
        # or higher on dst assessment
        if author_mode is self.RoBCopyAuthor.ORIGINAL:
            HAWCUser = apps.get_model("myuser", "HAWCUser")
            src_users = HAWCUser.objects.filter(riskofbiases__study__in=src_study_ids)
            src_user_ids = src_users.values_list("pk", flat=True)
            _filters = models.Q(assessment_teams__pk=dst_assessment_id) | models.Q(
                assessment_pms__pk=dst_assessment_id
            )
            dst_users = HAWCUser.objects.filter(_filters, pk__in=src_user_ids)
            dst_user_ids = dst_users.values_list("pk", flat=True)
            invalid_user_ids = set(src_user_ids) - set(dst_user_ids)
            if len(invalid_user_ids) > 0:
                raise ValidationError(
                    f"User id(s) {', '.join([str(id) for id in invalid_user_ids])} cannot be copied"
                )

    def bulk_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        dst_author,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        copy_mode: int,
        author_mode: int,
        **kwargs,
    ):
        """
        Bulk copy risk of bias data from source studies to destination studies.

        Args:
            src_assessment_id (int): Source assessment id
            dst_assessment_id (int): Destination assessment id
            dst_author (HAWCUser): Function calling user; will be
                used as risk of bias author if author_mode OTHER is used
            src_dst_study_ids (List[Tuple[int, int]]): Source study to destination study; format is [(src_study_id,dst_study_id),...]
            src_dst_metric_ids (List[Tuple[int, int]]): Source metric to destination metric; format is [(src_metric_id,dst_metric_id),...]
            copy_mode (int): Mode to use for RoB copy.
                1 for ORIGINAL, where riskofbias is copied 1 to 1
                2 for FINAL_AS_INITIAL, where final riskofbiases are set as active and non-final
            author_mode (int): Mode to use for RoB authors.
                1 for ORIGINAL, where original authors are used
                2 for OTHER, where dst_author is set as author for risk of bias data

        Returns:
            Tuple[int, Dict]: Log id and risk of bias mappings from source to destination. This log captures the returned mapping.
        """

        # validate the arguments
        self.validate_bulk_copy(
            src_assessment_id,
            dst_assessment_id,
            dst_author,
            src_dst_study_ids,
            src_dst_metric_ids,
            copy_mode,
            author_mode,
            **kwargs,
        )

        RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
        copy_mode = self.RoBCopyMode(copy_mode)
        author_mode = self.RoBCopyAuthor(author_mode)

        # create src to dst mapping
        src_to_dst = dict()
        # set mapping from arguments
        src_to_dst["study"] = {src: dst for src, dst in src_dst_study_ids}
        src_to_dst["metric"] = {src: dst for src, dst in src_dst_metric_ids}

        # get src riskofbiases
        src_study_ids = [src for src, _ in src_dst_study_ids]
        src_riskofbiases = self.get_queryset().filter(study_id__in=src_study_ids)
        src_riskofbias_ids = src_riskofbiases.values_list("pk", flat=True)
        # create new riskofbiases
        new_riskofbiases = []
        for riskofbias in src_riskofbiases:
            riskofbias.pk = None
            riskofbias.study_id = src_to_dst["study"][riskofbias.study_id]
            if author_mode is self.RoBCopyAuthor.OTHER:
                riskofbias.author = dst_author
            if copy_mode is self.RoBCopyMode.FINAL_AS_INITIAL:
                riskofbias.final = False
                riskofbias.active = True
            new_riskofbiases.append(riskofbias)
        dst_riskofbiases = self.bulk_create(new_riskofbiases)
        dst_riskofbias_ids = [obj.pk for obj in dst_riskofbiases]
        # add to mapping
        src_to_dst["riskofbias"] = {
            src: dst for src, dst in zip(src_riskofbias_ids, dst_riskofbias_ids)
        }

        # get src scores
        src_metric_ids = [src for src, _ in src_dst_metric_ids]
        src_scores = RiskOfBiasScore.objects.filter(
            riskofbias_id__in=src_riskofbias_ids, metric_id__in=src_metric_ids
        )
        src_score_ids = src_scores.values_list("pk", flat=True)
        # create new scores
        new_scores = []
        for score in src_scores:
            score.pk = None
            score.riskofbias_id = src_to_dst["riskofbias"][score.riskofbias_id]
            score.metric_id = src_to_dst["metric"][score.metric_id]
            new_scores.append(score)
        dst_scores = RiskOfBiasScore.objects.bulk_create(new_scores)
        dst_score_ids = [obj.pk for obj in dst_scores]
        # add to mapping
        src_to_dst["score"] = {src: dst for src, dst in zip(src_score_ids, dst_score_ids)}

        # log the src to dst mapping
        Log = apps.get_model("assessment", "Log")
        log = Log.objects.create(assessment_id=dst_assessment_id, message=json.dumps(src_to_dst),)
        return log.id, src_to_dst


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = "riskofbias__study__assessment"


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = "assessment"
