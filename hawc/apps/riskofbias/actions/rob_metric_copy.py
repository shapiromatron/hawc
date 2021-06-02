import json
from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.db import transaction
from django.db.models import IntegerChoices

from ..models import RiskOfBiasDomain, RiskOfBiasMetric


class RobMetricProfile(IntegerChoices):
    NTP_OHAT = 1, "NTP OHAT"
    EPA_IRIS = 2, "USEPA IRIS"

    def fixture_data(self) -> Dict:
        """Return fixture data as generated from data files."""
        _fixture = {
            self.NTP_OHAT: "ohat_study_quality_defaults.json",
            self.EPA_IRIS: "iris_study_quality_defaults.json",
        }
        p = Path(settings.PROJECT_PATH) / "apps/riskofbias/fixtures" / _fixture[self.value]
        return json.loads(p.read_text())


@transaction.atomic
def build_default(assessment_id: int, rob_type: RobMetricProfile):
    """
    Construct default risk of bias domains/metrics for an assessment.
    """
    data = rob_type.fixture_data()
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
