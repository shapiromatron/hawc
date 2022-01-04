import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.riskofbias.actions import RobApproach, clone_approach, load_approach
from hawc.apps.riskofbias.models import RiskOfBiasDomain, RiskOfBiasScore


@pytest.mark.django_db
def test_load_approach():
    assess_id = 1
    rob_score_qs = RiskOfBiasScore.objects.filter(riskofbias__study__assessment_id=assess_id)
    rob_domain_qs = RiskOfBiasDomain.objects.filter(
        assessment_id=assess_id, is_overall_confidence=True
    )
    # ensure initial state has evaluations and no overall domains
    assert rob_score_qs.count() > 0
    assert rob_domain_qs.count() == 1

    # there should be one overall domain
    load_approach(assess_id, RobApproach.EPA_IRIS)
    assert rob_score_qs.count() == 0
    assert rob_domain_qs.count() == 1

    # there should be no overall domains
    load_approach(assess_id, RobApproach.NTP_OHAT)
    assert rob_score_qs.count() == 0
    assert rob_domain_qs.count() == 0


@pytest.mark.django_db
def test_clone_approach():
    # ensure runs without failure
    dst = Assessment.objects.get(id=1)
    src = Assessment.objects.get(id=2)
    clone_approach(dst, src)
