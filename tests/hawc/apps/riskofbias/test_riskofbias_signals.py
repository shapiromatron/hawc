import pytest

from hawc.apps.common.signals import ignore_signals
from hawc.apps.riskofbias.models import RiskOfBiasMetric, RiskOfBiasScore


@pytest.mark.django_db
class TestMetricSignal:
    def test_signal(self):
        data = dict(
            name="demo",
            responses=1,
            domain_id=10,
            sort_order=10,
            required_animal=True,
            required_epi=False,
            required_invitro=False,
        )

        # without a signal, no scores created
        with ignore_signals():
            metric = RiskOfBiasMetric.objects.create(**data)
            qs = RiskOfBiasScore.objects.filter(metric=metric)
            assert qs.count() == 0

        # with signal, we create metrics
        metric = RiskOfBiasMetric.objects.create(**data)
        qs = RiskOfBiasScore.objects.filter(metric=metric)
        assert qs.count() == 3

    def test_create_by_requirements(self):
        data = dict(
            name="demo",
            responses=1,
            domain_id=10,
            sort_order=10,
            required_animal=False,
            required_epi=False,
            required_invitro=False,
        )

        metric = RiskOfBiasMetric.objects.create(**data)
        qs = RiskOfBiasScore.objects.filter(metric=metric)
        assert qs.count() == 0

        # check invitro
        metric.required_invitro = True
        metric.save()
        assert qs.count() == 1
        metric.required_invitro = False
        metric.save()
        assert qs.count() == 0

        # check epi
        metric.required_epi = True
        metric.save()
        assert qs.count() == 2
        metric.required_epi = False
        metric.save()
        assert qs.count() == 0

        # check animal
        metric.required_animal = True
        metric.save()
        assert qs.count() == 3
        metric.required_animal = False
        metric.save()
        assert qs.count() == 0
