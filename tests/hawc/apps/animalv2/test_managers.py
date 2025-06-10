import pytest

from hawc.apps.animalv2.models import Observation
from hawc.apps.vocab.constants import ObservationStatus
from hawc.apps.vocab.models import GuidelineProfile


@pytest.mark.django_db
class TestObservationManager:
    def test_default_observation(self):
        profile_nreq = GuidelineProfile.objects.get(id=1)

        # test not required with an existing endpoint
        default_observation = Observation.objects.default_observation(profile_nreq, endpoint=True)
        assert profile_nreq.obs_status == ObservationStatus.NR
        assert default_observation.tested_status
        assert default_observation.reported_status

        # test not required obs-status with no endpoint
        default_observation = Observation.objects.default_observation(profile_nreq, endpoint=False)
        assert not default_observation.tested_status
        assert not default_observation.reported_status

        # test recommended obs-status with endpoint
        profile_rec = GuidelineProfile.objects.get(id=3)
        default_observation = Observation.objects.default_observation(profile_rec, endpoint=True)
        assert not default_observation.tested_status
        assert default_observation.reported_status
