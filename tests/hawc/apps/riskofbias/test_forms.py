import pytest

from hawc.apps.riskofbias.forms import RoBMetricForm
from hawc.apps.riskofbias.models import RiskOfBiasMetric


@pytest.mark.django_db
class TestRoBMetricForm:
    def test_key(self):
        metric = RiskOfBiasMetric.objects.get(id=3)
        inputs = RoBMetricForm(instance=metric).initial

        # current form is valid
        form = RoBMetricForm(instance=metric, data=inputs)
        assert form.is_valid()

        # replacing with existing value fails
        inputs.update(key="demo-b")
        form = RoBMetricForm(instance=metric, data=inputs)
        assert RiskOfBiasMetric.objects.filter(
            domain__assessment=metric.domain.assessment_id, key="demo-b"
        ).exists()
        assert form.is_valid() is False
        assert form.errors == {"key": ["Key is not unique for assessment."]}
