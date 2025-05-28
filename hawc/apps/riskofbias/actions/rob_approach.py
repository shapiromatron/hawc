import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import IntegerChoices

from ...assessment.models import Assessment, Log
from ..models import RiskOfBias, RiskOfBiasAssessment, RiskOfBiasDomain, RiskOfBiasMetric


class RobApproach(IntegerChoices):
    NTP_OHAT = 1, "US NTP OHAT"
    EPA_IRIS = 2, "US EPA IRIS"

    def load_fixture_data(self) -> dict[str, Any]:
        """Return fixture data as generated from data files."""
        _fixture = {
            self.NTP_OHAT: "ohat_study_quality_defaults.json",
            self.EPA_IRIS: "iris_study_quality_defaults.json",
        }
        p = Path(settings.PROJECT_PATH) / "apps/riskofbias/fixtures" / _fixture[self.value]
        return json.loads(p.read_text())


@transaction.atomic
def load_approach(assessment_id: int, approach: RobApproach, user_id: int | None = None):
    """
    Construct default risk of bias domains/metrics for an assessment.
    """
    # fetch data
    data = approach.load_fixture_data()

    # log about changes being made
    domains = RiskOfBiasDomain.objects.filter(assessment_id=assessment_id)
    robs = RiskOfBias.objects.filter(study__assessment=assessment_id)
    log_message = dedent(
        f"""\
        Loading Risk of Bias approach {approach.name} into assessment {assessment_id}
        Deleting {domains.count()} RiskOfBiasDomain objects
        Deleting {robs.count()} RiskOfBias objects"""
    )
    Log.objects.create(assessment_id=assessment_id, user_id=user_id, message=log_message)

    # delete existing data (recursively deletes domains, metrics, scores, etc)
    domains.delete()
    robs.delete()

    # load help text
    settings = RiskOfBiasAssessment.objects.get(assessment_id=assessment_id)
    settings.help_text = data["help_text"]
    settings.save()

    # create domains and metrics
    metrics: list[RiskOfBiasMetric] = []
    for sort_order, domain_data in enumerate(data["domains"], start=1):
        metrics_data = domain_data.pop("metrics")
        domain = RiskOfBiasDomain.objects.create(
            assessment_id=assessment_id, sort_order=sort_order, **domain_data
        )
        metrics.extend(
            [
                RiskOfBiasMetric(domain_id=domain.id, sort_order=sort_order, **metric_data)
                for sort_order, metric_data in enumerate(metrics_data, start=1)
            ]
        )
    RiskOfBiasMetric.objects.bulk_create(metrics)


@transaction.atomic
def clone_approach(
    dest_assessment: Assessment, src_assessment: Assessment, user_id: int | None = None
) -> dict[int, int]:
    """
    Clone approach from one assessment to another.
    """

    # log about changes being made
    domains = dest_assessment.rob_domains.all()
    robs = RiskOfBias.objects.filter(study__assessment=dest_assessment)
    log_message = dedent(
        f"""\
        Cloning Risk of Bias approach: {src_assessment.id} -> {dest_assessment.id}
        Deleting {domains.count()} RiskOfBiasDomain objects
        Deleting {robs.count()} RiskOfBias objects"""
    )
    Log.objects.create(assessment=dest_assessment, user_id=user_id, message=log_message)

    # delete existing data (recursively deletes domains, metrics, scores, etc)
    domains.delete()
    robs.delete()

    # copy help-text
    dest_rob_settings = dest_assessment.rob_settings
    dest_rob_settings.help_text = src_assessment.rob_settings.help_text
    dest_rob_settings.save()

    # copy domains and metrics to assessment
    metric_map = {}
    for domain in src_assessment.rob_domains.all():
        metrics = list(domain.metrics.all())  # force evaluation
        domain.id = None
        domain.assessment = dest_assessment
        domain.save()
        for metric in metrics:
            src_metric_id = metric.id
            metric.id = None
            metric.domain = domain
            metric.save()
            metric_map[src_metric_id] = metric.id

    return metric_map
