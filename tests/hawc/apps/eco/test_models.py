import pytest

from hawc.apps.eco import models


class TestEcoModels:
    @pytest.mark.django_db
    def test_get_assessment(db_keys):
        for Model in [models.Design]:
            item = Model.objects.first()
            assert item.get_assessment().id == 2

        for Model in [models.Cause]:
            item = Model.objects.first()
            assert item.get_assessment().id == 2

        for Model in [models.Effect]:
            item = Model.objects.first()
            assert item.get_assessment().id == 2

        for Model in [models.Result]:
            item = Model.objects.first()
            assert item.get_assessment().id == 2

    @pytest.mark.django_db
    def test_get_study(db_keys):
        for Model in [models.Design]:
            item = Model.objects.first()
            assert item.get_study().id == 9

        for Model in [models.Cause]:
            item = Model.objects.first()
            assert item.get_study().id == 9

        for Model in [models.Effect]:
            item = Model.objects.first()
            assert item.get_study().id == 9

        for Model in [models.Result]:
            item = Model.objects.first()
            assert item.get_study().id == 9
