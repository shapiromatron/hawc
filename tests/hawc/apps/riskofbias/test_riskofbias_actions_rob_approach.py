import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.riskofbias.actions import RobApproach, clone_approach, load_approach


@pytest.mark.django_db
def test_load_approach():
    # ensure runs without failure
    load_approach(1, RobApproach.EPA_IRIS)
    load_approach(1, RobApproach.NTP_OHAT)


@pytest.mark.django_db
def test_clone_approach():
    # ensure runs without failure
    dst = Assessment.objects.get(id=1)
    src = Assessment.objects.get(id=2)
    clone_approach(dst, src)
