import pytest

from hawc.apps.animal.constants import DataType


class TestDataType:
    @pytest.mark.parametrize(
        ("data_type", "expected"),
        [
            (DataType.CONTINUOUS, True),
            (DataType.DICHOTOMOUS, True),
            (DataType.DICHOTOMOUS_CANCER, True),
            (DataType.PERCENT_DIFFERENCE, False),
        ],
    )
    def test_can_be_bmd_modelled(self, data_type, expected):
        assert data_type.can_be_bmd_modelled() is expected
