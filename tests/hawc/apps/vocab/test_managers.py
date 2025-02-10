import pytest

from hawc.apps.vocab.constants import ObservationStatus
from hawc.apps.vocab.models import GuidelineProfile, Observation, Term


@pytest.mark.django_db
class TestTermManager:
    def test_assessment_systems(self):
        assert Term.objects.assessment_systems(1).count() == 0

    def test_assessment_organs(self):
        assert Term.objects.assessment_organs(1).count() == 0

    def test_assessment_effects(self):
        assert Term.objects.assessment_effects(1).count() == 0

    def test_assessment_effect_subtypes(self):
        assert Term.objects.assessment_effect_subtypes(1).count() == 0

    def test_assessment_endpoint_names(self):
        assert Term.objects.assessment_endpoint_names(1).count() == 0


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


@pytest.mark.django_db
class TestGuidlineProfileManager:
    def test_guideline_id(self):
        guideline_id = GuidelineProfile.objects.get_guideline_id("Carcinogenicty")
        assert guideline_id == 9
