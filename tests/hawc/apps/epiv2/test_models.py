import pytest

from hawc.apps.epiv2 import models


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
