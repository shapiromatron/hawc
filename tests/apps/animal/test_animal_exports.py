from hawc.apps.animal.exports import get_significance_and_direction
from hawc.apps.animal.models import Endpoint


def test_get_significance_and_direction():
    # no data
    resp = get_significance_and_direction(Endpoint.DATA_TYPE_CONTINUOUS, [],)
    assert resp == []

    # continuous
    resp = get_significance_and_direction(
        Endpoint.DATA_TYPE_CONTINUOUS,
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
        Endpoint.DATA_TYPE_DICHOTOMOUS,
        [dict(significant=False), dict(significant=False), dict(significant=True)],
    )
    assert resp == ["No", "No", "Yes - ↑"]

    # percent diff
    resp = get_significance_and_direction(
        Endpoint.DATA_TYPE_CONTINUOUS,
        [
            dict(significant=False, response=0),
            dict(significant=False, response=0),
            dict(significant=True, response=0),
            dict(significant=True, response=-1),
            dict(significant=True, response=1),
        ],
    )
    assert resp == ["No", "No", "Yes - ?", "Yes - ↓", "Yes - ↑"]
