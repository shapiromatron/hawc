from ast import IsNot
from operator import is_not
import pytest

from hawc.apps.epiv2 import models


@pytest.mark.django_db
def test_get_assessment(db_keys):
    for Model in [models.StudyPopulationV2]:
        item = Model.objects.first()
        assert item.get_assessment().id == 1

