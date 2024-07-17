import json
from enum import IntEnum
from typing import Any

import pydantic

from hawc.apps.assessment.models import Assessment, Log
from hawc.apps.common.actions import BaseApiAction
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasMetric, RiskOfBiasScore
from hawc.apps.study.models import Study


class BulkCopyMode(IntEnum):
    ALL_ACTIVE = 1  # src active riskofbias -> dest active risk of bias
    FINAL_TO_INITIAL = 2  # src final riskofbias -> dest initial risk of bias


class BulkCopyAuthor(IntEnum):
    PRESERVE_ORIGINAL = 1  # original authors are preserved
    OVERWRITE = 2  # author for risk of bias data


class BulkRobCopyData(pydantic.BaseModel):
    src_assessment_id: int
    dst_assessment_id: int
    dst_author_id: int | None = None
    src_dst_study_ids: list[tuple[int, int]]
    src_dst_metric_ids: list[tuple[int, int]]
    copy_mode: BulkCopyMode
    author_mode: BulkCopyAuthor


class BulkRobCopyAction(BaseApiAction):
    """
    Copy final scores from a subset of studies from one assessment as the scores in a
    different assessment. Useful when an assessment is cloned or repurposed and existing
    evaluations are should be used in a new evaluation.
    """

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
        invalid_src_study_ids = Study.objects.invalid_ids(src_study_ids, assessment=src_assessment)
        if len(invalid_src_study_ids) > 0:
            msg = f"Invalid source study(ies) {', '.join([str(id) for id in invalid_src_study_ids])}; not found in assessment {self.inputs.src_assessment_id}"
            self.errors["src_dst_study_ids"].append(msg)

        # all dst studies from dst assessment
        invalid_dst_study_ids = Study.objects.invalid_ids(dst_study_ids, assessment=dst_assessment)
        if len(invalid_dst_study_ids) > 0:
            msg = f"Invalid destination study(ies) {', '.join([str(id) for id in invalid_dst_study_ids])}; not found in assessment {self.inputs.dst_assessment_id}"
            self.errors["src_dst_study_ids"].append(msg)

        # all src metrics from src studies should be given
        invalid_src_metric_ids = RiskOfBiasMetric.objects.invalid_ids(
            src_metric_ids, domain__assessment_id=self.inputs.src_assessment_id
        )
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
        invalid_dst_metric_ids = RiskOfBiasMetric.objects.invalid_ids(
            dst_metric_ids, domain__assessment_id=self.inputs.dst_assessment_id
        )
        if len(invalid_dst_metric_ids) > 0:
            msg = f"Invalid destination metric(s) {', '.join([str(id) for id in invalid_dst_metric_ids])}"
            self.errors["src_dst_metric_ids"].append(msg)

        # if overwriting, a valid author id must be provided
        if self.inputs.author_mode is BulkCopyAuthor.OVERWRITE:
            if self.inputs.dst_author_id is None:
                self.errors["dst_author_id"].append(
                    "dst_author_id required when author_mode overwrite."
                )
            else:
                dst_author = HAWCUser.objects.filter(id=self.inputs.dst_author_id).first()
                if dst_author is None:
                    self.errors["dst_author_id"].append("Author not found.")
                elif not dst_assessment.user_is_team_member_or_higher(dst_author):
                    msg = "Author is not part of destination assessment team."
                    self.errors["dst_author_id"].append(msg)

    def evaluate(self) -> dict[str, Any]:
        # create src to dst mapping
        src_to_dst = {}

        # set mapping from arguments
        src_to_dst["study"] = {src: dst for src, dst in self.inputs.src_dst_study_ids}
        src_to_dst["metric"] = {src: dst for src, dst in self.inputs.src_dst_metric_ids}

        src_study_ids, dst_study_ids = map(list, zip(*self.inputs.src_dst_study_ids, strict=True))

        # get src RiskOfBias
        filters = dict(study_id__in=src_study_ids, active=True)
        if self.inputs.copy_mode is BulkCopyMode.FINAL_TO_INITIAL:
            filters.update(final=True)
        src_riskofbiases = RiskOfBias.objects.filter(**filters)
        src_riskofbias_ids = src_riskofbiases.values_list("pk", flat=True)

        # create new RiskOfBias and add to mapping
        new_riskofbiases = []
        for riskofbias in src_riskofbiases:
            riskofbias.pk = None
            riskofbias.study_id = src_to_dst["study"][riskofbias.study_id]
            if self.inputs.author_mode is BulkCopyAuthor.OVERWRITE:
                riskofbias.author_id = self.inputs.dst_author_id
            if self.inputs.copy_mode is BulkCopyMode.FINAL_TO_INITIAL:
                riskofbias.final = False
            new_riskofbiases.append(riskofbias)

        if self.inputs.copy_mode is BulkCopyMode.ALL_ACTIVE:
            # make existing dst RiskOfBias inactive, since we're replacing with copies
            RiskOfBias.objects.filter(active=True, study_id__in=dst_study_ids).update(active=False)

        # copy new
        dst_riskofbiases = RiskOfBias.objects.bulk_create(new_riskofbiases)

        src_to_dst["riskofbias"] = {
            src: dst.pk for src, dst in zip(src_riskofbias_ids, dst_riskofbiases, strict=True)
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
        src_to_dst["score"] = {
            src: dst for src, dst in zip(src_score_ids, dst_score_ids, strict=True)
        }

        # log the src to dst mapping
        Log.objects.create(
            assessment_id=self.inputs.dst_assessment_id,
            message=json.dumps(src_to_dst),
        )
        return {"mapping": src_to_dst}

    def has_permission(self, request) -> tuple[bool, str]:
        """
        Check user is a project manager on both assessments.
        """
        src_assessment = Assessment.objects.filter(id=self.inputs.src_assessment_id).first()
        dst_assessment = Assessment.objects.filter(id=self.inputs.dst_assessment_id).first()
        if src_assessment is None or dst_assessment is None:
            return False, "Invalid source and/or destination assessment ID."
        if (
            src_assessment.user_is_project_manager_or_higher(request.user) is False
            or dst_assessment.user_is_project_manager_or_higher(request.user) is False
        ):
            return False, "Must be a Project Manager for source and destination assessments."
        return super().has_permission(request)
