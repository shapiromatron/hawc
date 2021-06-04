import json
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from django.db import transaction
from django.db.models import IntegerChoices

from ...assessment.models import Assessment
from ..models import RiskOfBiasAssessment, RiskOfBiasDomain, RiskOfBiasMetric


class RobApproach(IntegerChoices):
    NTP_OHAT = 1, "NTP OHAT"
    EPA_IRIS = 2, "USEPA IRIS"

    def load_fixture_data(self) -> Dict[str, Any]:
        """Return fixture data as generated from data files."""
        _fixture = {
            self.NTP_OHAT: "ohat_study_quality_defaults.json",
            self.EPA_IRIS: "iris_study_quality_defaults.json",
        }
        p = Path(settings.PROJECT_PATH) / "apps/riskofbias/fixtures" / _fixture[self.value]
        return json.loads(p.read_text())


@transaction.atomic
def load_approach(assessment_id: int, approach: RobApproach):
    """
    Construct default risk of bias domains/metrics for an assessment.
    """
    # fetch data
    data = approach.load_fixture_data()

    # delete existing data (recursively deletes domains, metrics, scores, etc)
    RiskOfBiasDomain.objects.filter(assessment_id=assessment_id).delete()

    # load help text
    settings = RiskOfBiasAssessment.objects.get(assessment_id=assessment_id)
    settings.help_text = data["help_text"]
    settings.save()

    # create domains and metrics
    metrics: List[RiskOfBiasMetric] = []
    for sort_order, domain_data in enumerate(data["domains"], start=1):
        domain = RiskOfBiasDomain.objects.create(
            assessment_id=assessment_id,
            sort_order=sort_order,
            name=domain_data["name"],
            description=domain_data["description"],
        )
        metrics.extend(
            [
                RiskOfBiasMetric(domain_id=domain.id, sort_order=sort_order, **metric_data)
                for sort_order, metric_data in enumerate(domain["metrics"], start=1)
            ]
        )
    RiskOfBiasMetric.objects.bulk_create(metrics)


@transaction.atomic
def clone_approach(dest_assessment: Assessment, src_assessment: Assessment):
    """
    Clone approach from one assessment to another.
    """
    # delete existing data (recursively deletes domains, metrics, scores, etc)
    dest_assessment.rob_domains.all().delete()

    # copy help-text
    dest_rob_settings = dest_assessment.rob_settings
    dest_rob_settings.help_text = src_assessment.rob_settings.help_text
    dest_rob_settings.save()

    # copy domains and metrics to assessment
    for domain in src_assessment.rob_domains.all():
        metrics = list(domain.metrics.all())  # force evaluation
        domain.id = None
        domain.assessment = dest_assessment
        domain.save()
        for metric in metrics:
            metric.id = None
            metric.domain = domain
            metric.save()
