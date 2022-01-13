import pytest

from hawc.apps.common.signals import ignore_signals
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasScore
from hawc.apps.study.models import Study


@pytest.mark.django_db
class TestMetricSignal:
    def test_signal(self):
        # setup
        with ignore_signals():
            study = Study.objects.create(
                assessment_id=2,
                short_citation="test",
                bioassay=False,
                epi=False,
                epi_meta=False,
                in_vitro=False,
            )
            RiskOfBias.objects.create(study=study, author_id=3, active=True)
            qs = RiskOfBiasScore.objects.filter(riskofbias__study=study)

            study.bioassay = True
            study.save()
            assert qs.count() == 0

            study.bioassay = False
            study.save()
            assert qs.count() == 0

        # with signal, we create metrics
        study.bioassay = True
        study.save()
        assert qs.count() == 2

    def test_create_by_requirements(self):
        # setup
        with ignore_signals():
            study = Study.objects.create(
                assessment_id=2,
                short_citation="test",
                bioassay=False,
                epi=False,
                epi_meta=False,
                in_vitro=False,
            )
            RiskOfBias.objects.create(study=study, author_id=3, active=True)
            qs = RiskOfBiasScore.objects.filter(riskofbias__study=study)

        # no signals; no data
        assert qs.count() == 0

        for fld in ("bioassay", "epi", "epi_meta", "in_vitro"):
            setattr(study, fld, True)
            study.save()
            assert qs.count() == 2

            setattr(study, fld, False)
            study.save()
            assert qs.count() == 0
