import json
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple

import pydantic
from django.db import models

from hawc.apps.assessment.models import Assessment, Log
from hawc.apps.common.api import ApiActionRequest
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasMetric, RiskOfBiasScore
from hawc.apps.study.models import Study


class RoBCopyMode(IntEnum):
    """Copy mode for bulk_copy"""

    ORIGINAL = 1  # src final riskofbias -> dest final risk of bias
    FINAL_AS_INITIAL = 2  # src final riskofbias -> dest initial risk of bias


class RoBCopyAuthor(IntEnum):
    """Author mode for bulk_copy"""

    PRESERVE_ORIGINAL = 1  # original authors are preserved
    OVERWRITE = 2  # author for risk of bias data


class BulkRobCopyData(pydantic.BaseModel):
    src_assessment_id: int
    dst_assessment_id: int
    dst_author_id: Optional[int]
    src_dst_study_ids: List[Tuple[int, int]]
    src_dst_metric_ids: List[Tuple[int, int]]
    copy_mode: RoBCopyMode
    author_mode: RoBCopyAuthor


class BulkRobCopy(ApiActionRequest):
    input_model = BulkRobCopyData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputs: BulkRobCopyData  # only done to set type inference

    def validate_business_logic(self):
        # check assessments
        if self.inputs.src_assessment_id == self.inputs.dst_assessment_id:
            self.errors["dst_assessment_id"].append(
                "Source and destination assessments must be different"
            )
        src_assessment = Assessment.objects.filter(id=self.inputs.src_assessment_id).first()

        if src_assessment is None:
            self.errors["src_assessment_id"].append("Invalid `src_assessment_id`")

        dst_assessment = Assessment.objects.filter(id=self.inputs.dst_assessment_id).first()
        if dst_assessment is None:
            self.errors["dst_assessment_id"].append("Invalid `dst_assessment_id`")

        # studies and metrics are unique
        src_study_ids = [src for src, _ in self.inputs.src_dst_study_ids]
        if len(src_study_ids) > len(set(src_study_ids)):
            self.errors["src_dst_study_ids"].append("Source study ids must be unique")
        dst_study_ids = [dst for _, dst in self.inputs.src_dst_study_ids]
        if len(dst_study_ids) > len(set(dst_study_ids)):
            self.errors["src_dst_study_ids"].append("Destination study ids must be unique")
        src_metric_ids = [src for src, _ in self.inputs.src_dst_metric_ids]
        if len(src_metric_ids) > len(set(src_metric_ids)):
            self.errors["src_dst_metric_ids"].append("Source metric ids must be unique")
        dst_metric_ids = [dst for _, dst in self.inputs.src_dst_metric_ids]
        if len(dst_metric_ids) > len(set(dst_metric_ids)):
            self.errors["src_dst_metric_ids"].append("Destination metric ids must be unique")

        # all src studies from src assessment
        src_studies = Study.objects.filter(pk__in=src_study_ids, assessment=src_assessment)
        invalid_src_study_ids = set(src_study_ids) - set(src_studies.values_list("pk", flat=True))
        if len(invalid_src_study_ids) > 0:
            msg = f"Invalid source study(ies) {', '.join([str(id) for id in invalid_src_study_ids])}; not found in assessment {self.inputs.src_assessment_id}"
            self.errors["src_dst_study_ids"].append(msg)

        # all dst studies from dst assessment
        dst_studies = Study.objects.filter(pk__in=dst_study_ids, assessment=dst_assessment)
        invalid_dst_study_ids = set(dst_study_ids) - set(dst_studies.values_list("pk", flat=True))
        if len(invalid_dst_study_ids) > 0:
            msg = f"Invalid destination study(ies) {', '.join([str(id) for id in invalid_dst_study_ids])}; not found in assessment {self.inputs.dst_assessment_id}"
            self.errors["src_dst_study_ids"].append(msg)

        # all src metrics from src studies should be given
        src_metrics = RiskOfBiasMetric.objects.filter(
            pk__in=src_metric_ids, domain__assessment_id=self.inputs.src_assessment_id
        )
        invalid_src_metric_ids = set(src_metric_ids) - set(src_metrics.values_list("pk", flat=True))
        if len(invalid_src_metric_ids) > 0:
            msg = (
                f"Invalid source metric(s) {', '.join([str(id) for id in invalid_src_metric_ids])}"
            )
            self.errors["src_dst_metric_ids"].append(msg)

        missing_src_metrics = RiskOfBiasMetric.objects.filter(
            domain__assessment_id=self.inputs.src_assessment_id
        ).exclude(pk__in=src_metric_ids)
        if missing_src_metrics.exists():
            msg = f"Need mapping for source metric(s) {', '.join([str(metric.pk) for metric in missing_src_metrics])}"
            self.errors["src_dst_metric_ids"].append(msg)

        # all dst metrics from dst assessment
        dst_metrics = RiskOfBiasMetric.objects.filter(
            pk__in=dst_metric_ids, domain__assessment_id=self.inputs.dst_assessment_id
        )
        invalid_dst_metric_ids = set(dst_metric_ids) - set(dst_metrics.values_list("pk", flat=True))
        if len(invalid_dst_metric_ids) > 0:
            msg = f"Invalid destination metric(s) {', '.join([str(id) for id in invalid_dst_metric_ids])}"
            self.errors["src_dst_metric_ids"].append(msg)

        # all users who authored src riskofbiases are team member or higher on dst assessment
        if self.inputs.author_mode is RoBCopyAuthor.PRESERVE_ORIGINAL:
            src_user_ids = (
                RiskOfBias.objects.filter(study__in=src_study_ids, active=True, final=True)
                .order_by("author_id")
                .distinct("author_id")
                .values_list("author_id", flat=True)
            )
            _filters = models.Q(assessment_teams=dst_assessment) | models.Q(
                assessment_pms=dst_assessment
            )
            dst_user_ids = HAWCUser.objects.filter(_filters, pk__in=src_user_ids).values_list(
                "pk", flat=True
            )
            invalid_user_ids = set(src_user_ids) - set(dst_user_ids)
            if len(invalid_user_ids) > 0:
                msg = f"User id(s) {', '.join([str(id) for id in invalid_user_ids])} not found in destination"
                self.errors["user_ids"].append(msg)

        # if overwriting, a valid author id must be provided
        if self.inputs.author_mode is RoBCopyAuthor.OVERWRITE and self.inputs.dst_author_id is None:
            self.errors["dst_author_id"].append("Author required when overwriting")
            dst_author = HAWCUser.objects.filter(id=self.inputs.dst_author_id).first()

            if dst_author is None:
                self.errors["dst_author_id"].append("Author not found.")

            if not dst_assessment.user_is_team_member_or_higher(dst_author):
                msg = "Author is not part of destination assessment team."
                self.errors["dst_author_id"].append(msg)

    def evaluate(self) -> Dict[str, Any]:
        # create src to dst mapping
        src_to_dst = {}

        # set mapping from arguments
        src_to_dst["study"] = {src: dst for src, dst in self.inputs.src_dst_study_ids}
        src_to_dst["metric"] = {src: dst for src, dst in self.inputs.src_dst_metric_ids}

        src_study_ids, dst_study_ids = map(list, zip(*self.inputs.src_dst_study_ids))

        # make existing dst RiskOfBias inactive
        RiskOfBias.objects.filter(study_id__in=dst_study_ids).update(active=False)

        # get src RiskOfBias
        src_riskofbiases = RiskOfBias.objects.filter(
            study_id__in=src_study_ids, active=True, final=True
        )
        src_riskofbias_ids = src_riskofbiases.values_list("pk", flat=True)

        # create new RiskOfBias and add to mapping
        new_riskofbiases = []
        for riskofbias in src_riskofbiases:
            riskofbias.pk = None
            riskofbias.study_id = src_to_dst["study"][riskofbias.study_id]
            if self.inputs.author_mode is RoBCopyAuthor.OVERWRITE:
                riskofbias.author_id = self.inputs.dst_author_id
            if self.inputs.copy_mode is RoBCopyMode.FINAL_AS_INITIAL:
                riskofbias.final = False
            new_riskofbiases.append(riskofbias)
        dst_riskofbiases = RiskOfBias.objects.bulk_create(new_riskofbiases)
        src_to_dst["riskofbias"] = {
            src: dst.pk for src, dst in zip(src_riskofbias_ids, dst_riskofbiases)
        }

        # get RiskOfBiasScore
        src_metric_ids = [src_id for src_id, _ in self.inputs.src_dst_metric_ids]
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
        log = Log.objects.create(
            assessment_id=self.inputs.dst_assessment_id, message=json.dumps(src_to_dst),
        )
        return {"log_id": log.id, "log_url": log.get_api_url(), "mapping": src_to_dst}
