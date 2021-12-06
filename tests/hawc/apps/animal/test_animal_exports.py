from hawc.apps.animal.constants import DataType
from hawc.apps.animal.exports import EndpointFlatDataPivot, get_significance_and_direction


def test_get_significance_and_direction():
    # no data
    resp = get_significance_and_direction(DataType.C, [],)
    assert resp == []

    # continuous
    resp = get_significance_and_direction(
        DataType.C,
        [
            dict(significant=False, response=0),
            dict(significant=False, response=1),
            dict(significant=True, response=0),
            dict(significant=True, response=-1),
            dict(significant=True, response=1),
        ],
    )
    assert resp == ["No", "No", "Yes - ?", "Yes - ↓", "Yes - ↑"]

    # dichotomous
    resp = get_significance_and_direction(
        DataType.D,
        [
            dict(percent_affected=0, significant=False),
            dict(percent_affected=10, significant=False),
            dict(percent_affected=20, significant=True),
        ],
    )
    assert resp == ["No", "No", "Yes - ↑"]

    resp = get_significance_and_direction(
        DataType.DC,
        [
            dict(percent_affected=50, significant=False),
            dict(percent_affected=40, significant=False),
            dict(percent_affected=30, significant=True),
        ],
    )
    assert resp == ["No", "No", "Yes - ↓"]

    # percent diff
    resp = get_significance_and_direction(
        DataType.C,
        [
            dict(significant=False, response=0),
            dict(significant=False, response=0),
            dict(significant=True, response=0),
            dict(significant=True, response=-1),
            dict(significant=True, response=1),
        ],
    )
    assert resp == ["No", "No", "Yes - ?", "Yes - ↓", "Yes - ↑"]


class TestEndpointFlatDataPivot:
    def test_dose_low_high(self):
        # returns a tuple of the lowest non-zero dose
        # and the highest dose
        func = EndpointFlatDataPivot._dose_low_high

        # all of these doses are present
        valid_doses = [0.0, 1.0, 20.0, 300.0]
        (low, high) = func(valid_doses)
        assert low == 1.0 and high == 300.0

        # if a dose is not present, it will be None
        one_invalid_dose = [0.0, 1.0, None, 300.0]
        (low, high) = func(one_invalid_dose)
        assert low == 1.0 and high == 300.0

        # missing doses can affect lowest dose
        invalid_low_dose = [0.0, None, 20.0, 300.0]
        (low, high) = func(invalid_low_dose)
        assert low == 20.0 and high == 300.0

        # missing doses can affect highest dose
        invalid_high_dose = [0.0, 1.0, 20.0, None]
        (low, high) = func(invalid_high_dose)
        assert low == 1.0 and high == 20.0

        # if only one valid dose, it will be both lowest and highest
        one_valid_dose = [0.0, None, 20.0, None]
        (low, high) = func(one_valid_dose)
        assert low == 20.0 and high == 20.0

        # if no valid dose, lowest and highest is None
        invalid_doses = [0.0, None, None, None]
        (low, high) = func(invalid_doses)
        assert low is None and high is None

    def test_dose_is_reported(self):
        func = EndpointFlatDataPivot._dose_is_reported

        # check that dose is reported even when value is falsy but not None
        assert func(1, [dict(dose_group_id=1, n=0)]) is True
        assert func(1, [dict(dose_group_id=1, response=0)]) is True
        assert func(1, [dict(dose_group_id=1, incidence=0)]) is True

        assert func(1, []) is False
        assert func(1, [dict(dose_group_id=1)]) is False
        assert func(1, [dict(dose_group_id=1, n=None, response=None, incidence=None)]) is False
