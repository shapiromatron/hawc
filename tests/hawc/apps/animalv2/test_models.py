import pytest

from hawc.apps.animalv2 import models


class TestAnimalV2Models:
    @pytest.mark.django_db
    def test_get_assessment(db_keys):
        for Model in [models.Experiment]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Chemical]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.AnimalGroup]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Treatment]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.DoseGroup]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Endpoint]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.ObservationTime]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.DataExtraction]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.DoseResponseGroupLevelData]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.DoseResponseAnimalLevelData]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

    @pytest.mark.django_db
    def test_get_study(db_keys):
        for Model in [models.Experiment]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Chemical]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.AnimalGroup]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Treatment]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.DoseGroup]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Endpoint]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.ObservationTime]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.DataExtraction]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.DoseResponseGroupLevelData]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.DoseResponseAnimalLevelData]:
            item = Model.objects.first()
            assert item.get_study().id == 1


@pytest.mark.django_db
class TestObservation:
    def test_attributes(self):
        observation = models.Observation.objects.get(id=1)
        assert str(observation) == "Test Experiment:ToxRefDB::effect_subtype::eye"
