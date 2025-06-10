import pytest

from hawc.apps.animalv2.models import Term


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
