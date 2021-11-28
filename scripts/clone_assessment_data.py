import json
import logging
import os
import sys
from collections import defaultdict
from itertools import chain
from pathlib import Path
from typing import Dict, List

import django
from animal import models as ani_models
from animal import signals as ani_signals
from assessment import signals as assess_signals
from assessment.models import Assessment
from bmd import models as bmd_models
from bmd import signals as bmd_signals
from django.core import management
from django.db import transaction
from django.db.models import Model
from django.db.models.signals import post_save
from epi import models as epi_models
from epi import signals as epi_signals
from invitro import models as iv_models
from lit import models as lit_models
from lit import signals as lit_signals
from riskofbias import models as rob_models
from riskofbias import signals as rob_signals
from study import models as study_models
from study import signals as study_signals
from summary import models as summary_models

ROOT = str(Path(__file__).parents[0].resolve())
sys.path.append(ROOT)
os.chdir(ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.dev")
django.setup()
logger = logging.getLogger(__name__)


class Cloner:

    M2M_FIELDS: List[str] = []

    def _set_overrides(self, obj, overrides):
        if overrides is not None:
            for key, val in overrides.items():
                setattr(obj, key, val)

    def _get_m2m(self, obj: Model) -> Dict[str, List[Model]]:
        fields = {}
        for field in self.M2M_FIELDS:
            fields[field] = list(getattr(obj, field).all())
        return fields

    def _set_m2m(self, obj: Model, fields: Dict):
        for name, values in fields.items():
            getattr(obj, name).set(values)

    def clone(self, obj: Model, overrides: Dict = None) -> Model:
        logger.info(f"Cloning: #{obj.id}: {obj}")
        m2ms = self._get_m2m(obj)
        obj.pk = None
        self._set_overrides(obj, overrides)
        obj.save()
        self._set_m2m(obj, m2ms)
        return obj


class AssessmentCloner(Cloner):
    M2M_FIELDS = ["project_manager", "team_members", "reviewers"]


def disable_signals():
    assert (
        post_save.disconnect(receiver=assess_signals.default_configuration, sender=Assessment)
        is True
    )
    assert (
        post_save.disconnect(
            receiver=lit_signals.invalidate_study_cache, sender=lit_models.Reference
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=lit_signals.invalidate_tag_cache, sender=lit_models.ReferenceFilterTag,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.invalidate_caches_rob_metrics, sender=rob_models.RiskOfBiasDomain,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.invalidate_caches_rob_metrics, sender=rob_models.RiskOfBiasMetric,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.create_rob_scores, sender=rob_models.RiskOfBiasMetric
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.update_study_type_metrics, sender=rob_models.RiskOfBiasMetric,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=bmd_signals.invalidate_outcome_cache, sender=bmd_models.SelectedModel,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=study_signals.update_study_rob_scores, sender=study_models.Study
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=study_signals.invalidate_caches_study, sender=study_models.Study
        )
        is True
    )
    assert (
        post_save.disconnect(receiver=study_signals.create_study_tasks, sender=study_models.Study)
        is True
    )
    assert (
        post_save.disconnect(
            receiver=ani_signals.invalidate_endpoint_cache, sender=ani_models.Experiment
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=ani_signals.invalidate_endpoint_cache, sender=ani_models.AnimalGroup,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=ani_signals.invalidate_endpoint_cache, sender=ani_models.DosingRegime,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=ani_signals.invalidate_endpoint_cache, sender=ani_models.Endpoint
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=ani_signals.invalidate_endpoint_cache, sender=ani_models.EndpointGroup,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.invalidate_caches_risk_of_bias, sender=rob_models.RiskOfBias,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=rob_signals.invalidate_caches_risk_of_bias, sender=rob_models.RiskOfBiasScore,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.StudyPopulation,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.ComparisonSet,
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.Exposure
        )
        is True
    )
    assert (
        post_save.disconnect(receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.Group)
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.Outcome
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.Result
        )
        is True
    )
    assert (
        post_save.disconnect(
            receiver=epi_signals.invalidate_outcome_cache, sender=epi_models.GroupResult
        )
        is True
    )
    assert (
        post_save.disconnect(receiver=epi_signals.modify_group_result, sender=epi_models.Group)
        is True
    )


def apply_lit_tags(study_ids: List[int], cw: Dict):
    # apply the same literature tags previously used in original studies to clones
    lit_models.ReferenceTags.objects.bulk_create(
        [
            lit_models.ReferenceTags(
                tag_id=cw["ref-filter-tags"][tag.tag_id],
                content_object_id=cw["studies"][tag.content_object_id],
            )
            for tag in lit_models.ReferenceTags.objects.filter(content_object_id__in=study_ids)
        ]
    )


def apply_ivcategory_tags(study_ids: List[int], cw: Dict):
    raise NotImplementedError("TODO - implement - not needed for this assessment.")


@transaction.atomic
def clone_assessment(
    old_assessment_id: int,
    new_assessment_name: str,
    study_ids: List[int],
    dp_ids: List[int],
    viz_ids: List[int],
):

    # clone assessment stuff
    # disable post_create signals
    assessment_cloner = AssessmentCloner()

    new_assessment = assessment_cloner.clone(
        Assessment.objects.get(id=old_assessment_id), {"name": new_assessment_name}
    )
    new_assessment_id = new_assessment.id
    old_assessment = Assessment.objects.get(id=old_assessment_id)

    # build defaults - NOT copied
    summary_models.SummaryText.build_default(new_assessment)

    cw = defaultdict(dict)
    cw[Assessment.COPY_NAME][old_assessment_id] = new_assessment_id

    cw["ref-filter-tags"] = lit_models.ReferenceFilterTag.copy_tags(
        old_assessment.id, new_assessment.id
    )
    lit_models.Search.build_default(new_assessment)

    cw["iv-endpoint-categories"] = iv_models.IVEndpointCategory.copy_tags(
        old_assessment.id, new_assessment.id,
    )

    # copy rob logic
    old_assessment.rob_settings.copy_across_assessments(cw)
    for domain in old_assessment.rob_domains.all():
        domain.copy_across_assessments(cw)

    # copy bmd logic
    old_assessment.bmd_settings.copy_across_assessments(cw)
    for bmd_logic_field in old_assessment.bmd_logic_fields.all():
        bmd_logic_field.copy_across_assessments(cw)

    # copy study data
    studies = study_models.Study.objects.filter(id__in=study_ids).order_by("id")
    assert studies.count() == len(studies)
    cw = study_models.Study.copy_across_assessment(
        studies=studies, assessment=new_assessment, cw=cw, copy_rob=True
    )

    apply_lit_tags(study_ids, cw)
    # apply_ivcategory_tags(study_ids, cw)

    # copy viz
    visuals = summary_models.Visual.objects.filter(id__in=viz_ids).order_by("id")
    assert visuals.count() == len(viz_ids)
    for visual in visuals:
        visual.copy_across_assessments(cw)

    # copy data-pivots
    dpus = summary_models.DataPivotUpload.objects.filter(id__in=dp_ids).order_by("id")
    dpqs = summary_models.DataPivotQuery.objects.filter(id__in=dp_ids).order_by("id")
    assert dpus.count() + dpqs.count() == len(dp_ids)
    for dp in chain(dpus, dpqs):
        dp.copy_across_assessments(cw)

    with open(f"{new_assessment_name}.json", "w") as f:
        json.dump(cw, f, indent=True)


if __name__ == "__main__":
    disable_signals()
    clone_assessment(1, "new-one", [1, 2, 3], [4, 5, 6], [7, 8, 9])
    management.call_command("clear_cache")
