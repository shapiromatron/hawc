import pytest

from hawc.apps.animal import models


def _check_percent_control(inputs, outputs, data_type):
    data = [{"n": el[1], "response": el[2], "stdev": el[3]} for el in inputs]
    models.EndpointGroup.percentControl(data_type, data)
    for i, d in enumerate(outputs):
        if outputs[i][0] is None:
            assert outputs[i][0] == data[i]["percentControlMean"]
        else:
            assert outputs[i][0] == pytest.approx(data[i]["percentControlMean"])

        if outputs[i][1] is None:
            assert outputs[i][1] == data[i]["percentControlLow"]
        else:
            assert outputs[i][1] == pytest.approx(data[i]["percentControlLow"])

        if outputs[i][2] is None:
            assert outputs[i][2] == data[i]["percentControlHigh"]
        else:
            assert outputs[i][2] == pytest.approx(data[i]["percentControlHigh"])


def test_endpoint_group_percent_control():
    # increasing
    inputs = [
        (0, 10, 15.1, 3.5),
        (100, 9, 25.5, 7.8),
        (200, 8, 35.7, 13.3),
        (300, 7, 150.1, 23.1),
    ]
    outputs = [
        (0.0, -20.3171209611, 20.3171209611),
        (68.8741721854, 27.3103479282, 110.437996443),
        (136.42384106, 66.5736748386, 206.274007281),
        (894.039735099, 711.728201234, 1076.35126896),
    ]
    _check_percent_control(inputs, outputs, "C")

    # decreasing
    inputs = [
        (0, 7, 150.1, 15.1),
        (100, 8, 35.7, 13.3),
        (200, 9, 25.5, 7.8),
        (300, 10, 15.1, 3.5),
    ]
    outputs = [
        (0.0, -10.5394586484, 10.5394586484),
        (-76.2158560959, -82.6067710106, -69.8249411813),
        (-83.0113257828, -86.634786933, -79.3878646326),
        (-89.9400399734, -91.5681779063, -88.3119020404),
    ]
    _check_percent_control(inputs, outputs, "C")

    # edge case
    inputs = [
        (0, 7, 150.1, 15.1),
        (100, 7, 150.1, 15.1),
        (200, 700, 150.1, 15.1),
        (300, 10, 0, 15),
    ]
    outputs = [
        (0.0, -10.5394586484, 10.5394586484),
        (0.0, -10.5394586484, 10.5394586484),
        (0.0, -7.48969260009, 7.48969260009),
        (None, None, None),
    ]
    _check_percent_control(inputs, outputs, "C")

    # none cases
    inputs = [
        (0, 7, 150.1, None),
        (0, 7, 0, 3),
    ]
    outputs = [
        (0.0, None, None),
        (None, None, None),
    ]
    _check_percent_control(inputs, outputs, "C")

    inputs = [
        (0, 7, 0, 3),
        (0, 7, 150.1, None),
    ]
    outputs = [
        (None, None, None),
        (None, None, None),
    ]
    _check_percent_control(inputs, outputs, "C")


def test_percent_control():
    egs = [{"response": 1, "lower_ci": 2, "upper_ci": 3}]
    models.EndpointGroup.percentControl("P", egs)
    assert 1 == pytest.approx(egs[0]["percentControlMean"])
    assert 2 == pytest.approx(egs[0]["percentControlLow"])
    assert 3 == pytest.approx(egs[0]["percentControlHigh"])
