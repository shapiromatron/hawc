import pytest
from django.apps import apps

from hawc.apps.epiv2 import models


@pytest.mark.skipif(
    apps.is_installed("hawc.apps.epiv2") is False,
    reason="epi v2 is not installed in your environment",
)
class TestEpiV2Models:
    @pytest.mark.django_db
    def test_get_assessment(db_keys):
        for Model in [models.Design]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Chemical]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Criteria]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Exposure]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.ExposureLevel]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.Outcome]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.AdjustmentFactor]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

        for Model in [models.DataExtraction]:
            item = Model.objects.first()
            assert item.get_assessment().id == 1

    @pytest.mark.django_db
    def test_get_study(db_keys):
        for Model in [models.Design]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Chemical]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Criteria]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Exposure]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.ExposureLevel]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.Outcome]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.AdjustmentFactor]:
            item = Model.objects.first()
            assert item.get_study().id == 1

        for Model in [models.DataExtraction]:
            item = Model.objects.first()
            assert item.get_study().id == 1
