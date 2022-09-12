import pytest

from hawc.apps.animal import models


@pytest.mark.django_db
class TestAnimalGroup:
    def test_can_delete(self):
        # TODO - add
        assert 1 == 2


@pytest.mark.django_db
class TestEndpoint:
    def test_save(self, db_keys):
        # make sure our strip() methods work
        instance = models.Endpoint.objects.get(id=db_keys.endpoint_working)
        assert instance.system == ""
        instance.system = "   "
        instance.save()
        assert instance.system == ""


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


class TestConfidenceIntervalsMixin:
    def testGetConfidenceIntervals_continuous(self):
        # test invalid data
        data = [
            {"n": None, "response": 10, "stdev": 1},
            {"n": 0, "response": 10, "stdev": 1},
            {"n": 30, "response": None, "stdev": 1},
            {"n": 30, "response": 10, "stdev": None},
        ]
        models.ConfidenceIntervalsMixin.getConfidenceIntervals("C", data)
        for item in data:
            assert "lower_ci" not in item
            assert "upper_ci" not in item

        # test valid data
        data = [
            {"n": 30, "response": 10, "stdev": 1},
            {"n": 10, "response": 10, "stdev": 1},
        ]
        models.ConfidenceIntervalsMixin.getConfidenceIntervals("C", data)
        lowers = list(map(lambda d: d["lower_ci"], data))
        uppers = list(map(lambda d: d["upper_ci"], data))
        assert pytest.approx([9.62, 9.28], abs=0.1) == lowers
        assert pytest.approx([10.37, 10.72], abs=0.1) == uppers

    def testGetConfidenceIntervals_dichtomous(self):
        # test invalid data
        data = [
            {"n": None, "incidence": 10},
            {"n": 0, "incidence": 10},
            {"n": 30, "incidence": None},
        ]
        models.ConfidenceIntervalsMixin.getConfidenceIntervals("D", data)
        for item in data:
            assert "lower_ci" not in item
            assert "upper_ci" not in item

        # test valid data
        data = [
            {"n": 10, "incidence": 0},
            {"n": 10, "incidence": 10},
            {"n": 100, "incidence": 0},
            {"n": 100, "incidence": 100},
        ]
        models.ConfidenceIntervalsMixin.getConfidenceIntervals("D", data)
        lowers = list(map(lambda d: d["lower_ci"], data))
        uppers = list(map(lambda d: d["upper_ci"], data))
        assert pytest.approx([0.0092, 0.6554, 0.0009, 0.9538], abs=0.001) == lowers
        assert pytest.approx([0.3474, 0.9960, 0.0461, 0.9991], abs=0.001) == uppers


@pytest.mark.django_db
def test_heatmap_df(db_keys):
    df = models.Endpoint.heatmap_df(db_keys.assessment_final, True)
    expected_columns = [
        "study id",
        "study citation",
        "study identifier",
        "overall study evaluation",
        "experiment id",
        "experiment name",
        "experiment type",
        "treatment period",
        "experiment cas",
        "experiment dtxsid",
        "experiment chemical",
        "animal group id",
        "animal group name",
        "animal description",
        "animal description, with n",
        "species",
        "strain",
        "sex",
        "generation",
        "route of exposure",
        "endpoint id",
        "system",
        "organ",
        "effect",
        "effect subtype",
        "endpoint name",
        "observation time",
    ]
    assert df.columns.tolist() == expected_columns
