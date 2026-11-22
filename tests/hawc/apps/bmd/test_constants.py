import pybmds
import pytest
from model_bakery import baker
from pybmds.constants import Dtype

from hawc.apps.animal.constants import DataType
from hawc.apps.bmd.constants import (
    BmdInputSettings,
    ContinuousInputSettings,
    DichotomousInputSettings,
    SelectedModel,
    bmds2_defaults,
    get_input_options,
)


def prepare_endpoint(data_type: str, dose_units_id: int = 123):
    """Build an unsaved Endpoint with cached doses, avoiding any database access."""
    endpoint = baker.prepare("animal.Endpoint", data_type=data_type)
    endpoint.doses = [{"id": dose_units_id, "name": "mg/kg", "values": [0, 1, 10]}]
    return endpoint


@pytest.fixture
def dichotomous() -> pybmds.Session:
    dataset = pybmds.DichotomousDataset(doses=[0, 1, 2, 3], ns=[10] * 4, incidences=[0, 1, 3, 6])
    return pybmds.Session(dataset=dataset)


@pytest.fixture
def continuous() -> pybmds.Session:
    dataset = pybmds.ContinuousDataset(
        doses=[0, 1, 2, 3], ns=[10] * 4, means=[1, 2, 3, 5], stdevs=[1] * 4
    )
    return pybmds.Session(dataset=dataset)


def test_bmds2_defaults():
    assert isinstance(bmds2_defaults(), dict)


class TestDichotomousInputSettings:
    def test_add_models(self, dichotomous):
        DichotomousInputSettings(dose_units_id=1).add_models(dichotomous)
        assert len(dichotomous.models) == 11
        assert all(
            m.settings.bmr_type == pybmds.DichotomousRiskType.ExtraRisk for m in dichotomous.models
        )
        assert all(m.settings.bmr == 0.1 for m in dichotomous.models)


class TestContinuousInputSettings:
    def test_add_models(self, continuous):
        ContinuousInputSettings(dose_units_id=1).add_models(continuous)
        assert len(continuous.models) == 7
        assert all(
            m.settings.bmr_type == pybmds.ContinuousRiskType.StandardDeviation
            for m in continuous.models
        )
        assert all(m.settings.bmr == 1 for m in continuous.models)


class TestBmdInputSettings:
    def test_add_models(self, continuous):
        settings = BmdInputSettings(
            dtype=Dtype.CONTINUOUS, settings=ContinuousInputSettings(dose_units_id=1)
        )
        settings.add_models(continuous)
        assert len(continuous.models) == 7

    @pytest.mark.parametrize(
        ("data_type", "dtype", "settings_class"),
        [
            (DataType.DICHOTOMOUS, Dtype.DICHOTOMOUS, DichotomousInputSettings),
            (DataType.DICHOTOMOUS_CANCER, Dtype.DICHOTOMOUS, DichotomousInputSettings),
            (DataType.CONTINUOUS, Dtype.CONTINUOUS, ContinuousInputSettings),
        ],
    )
    def test_create_default(self, data_type, dtype, settings_class):
        settings = BmdInputSettings.create_default(prepare_endpoint(data_type))
        assert settings.dtype == dtype
        assert isinstance(settings.settings, settings_class)
        assert settings.settings.dose_units_id == 123

    def test_create_default_invalid(self):
        endpoint = prepare_endpoint(DataType.PERCENT_DIFFERENCE)
        with pytest.raises(ValueError, match="Cannot create default"):
            BmdInputSettings.create_default(endpoint)


class TestGetInputOptions:
    @pytest.mark.parametrize(
        ("data_type", "expected_dtype", "n_bmr_types", "n_dist_types"),
        [
            (DataType.CONTINUOUS, DataType.CONTINUOUS, 3, 2),
            (DataType.DICHOTOMOUS, DataType.DICHOTOMOUS, 2, None),
            (DataType.DICHOTOMOUS_CANCER, DataType.DICHOTOMOUS, 2, None),
        ],
    )
    def test_valid(self, data_type, expected_dtype, n_bmr_types, n_dist_types):
        options = get_input_options(data_type)
        assert options["dtype"] == expected_dtype
        assert len(options["bmr_types"]) == n_bmr_types
        assert (len(options["dist_types"]) if "dist_types" in options else None) == n_dist_types

    def test_invalid(self):
        with pytest.raises(ValueError, match="Unknown data type"):
            get_input_options("invalid")


class TestSelectedModel:
    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            ({}, {"model_index": None, "notes": ""}),
            ({"model_index": 3, "notes": "abc"}, {"model_index": 3, "notes": "abc"}),
        ],
    )
    def test_to_bmd_output(self, kwargs, expected):
        assert SelectedModel(**kwargs).to_bmd_output() == expected
