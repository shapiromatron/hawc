import pytest

from hawc.apps.riskofbias.models import RiskOfBiasMetric, RiskOfBiasScore


@pytest.mark.django_db
def test_update_study_type_metrics():
    # without a signal, no scores would be created; check that signal creates scores
    metric = RiskOfBiasMetric.objects.create(name="demo", responses=1, domain_id=10, sort_order=10)
    assert RiskOfBiasScore.objects.filter(metric=metric).count() > 0
