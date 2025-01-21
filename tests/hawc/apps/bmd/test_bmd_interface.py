import pytest

from hawc.apps.animal.models import Endpoint
from hawc.apps.bmd.bmd_interface import build_dataset


@pytest.mark.django_db
def test_build_dataset():
    endpoint = Endpoint.objects.get(id=12)
    dataset = build_dataset(endpoint=endpoint, dose_units_id=1, n_drop_doses=0)
    assert dataset.num_dose_groups == 5

    dataset = build_dataset(endpoint=endpoint, dose_units_id=1, n_drop_doses=1)
    assert dataset.num_dose_groups == 4

    dataset = build_dataset(endpoint=endpoint, dose_units_id=1, n_drop_doses=2)
    assert dataset.num_dose_groups == 3
