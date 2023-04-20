import json
from functools import lru_cache
from pathlib import Path

from bmds import constants
from bmds.bmds3.constants import DistType
from bmds.bmds3.types.continuous import ContinuousRiskType
from bmds.bmds3.types.dichotomous import DichotomousRiskType
from django.db import models
from django.db.models import IntegerChoices
from pydantic import BaseModel, Field, confloat, conint

from ..animal.constants import DataType
from ..animal.models import Endpoint


class BmdsVersion(models.TextChoices):
    BMDS2601 = "BMDS2601", "BMDS 2.6.0.1"
    BMDS270 = "BMDS270", "BMDS 2.7"
    BMDS330 = "BMDS330", "BMDS 3.3 (2022.10)"


@lru_cache
def bmds2_logic() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "logic.json").read_text())["objects"]


class DichtomoumsBmrChoices(IntegerChoices):
    Extra = DichotomousRiskType.ExtraRisk.value, "Extra Risk"
    Added = DichotomousRiskType.AddedRisk.value, "Added Risk"


class ContinuousBmrChoices(IntegerChoices):
    StandardDeviation = ContinuousRiskType.StandardDeviation.value, "Standard Deviation"
    RelativeDeviation = ContinuousRiskType.RelativeDeviation.value, "Relative Deviation"
    AbsoluteDeviation = ContinuousRiskType.AbsoluteDeviation.value, "Absolute Deviation"


class ContinuousDistTypeChoices(IntegerChoices):
    normal = DistType.normal.value, "Constant"
    normal_ncv = DistType.normal_ncv.value, "Non-constant"


class DichotomousInputSettings(BaseModel):
    dose_units_id: int
    num_doses_dropped: conint(ge=0) = 0
    bmr_type: DichotomousRiskType = DichotomousRiskType.ExtraRisk
    bmr_value: confloat(gt=0) = 0.1

    def add_models(self, session):
        settings = {"bmr_type": self.bmr_type, "bmr": self.bmr_value}
        session.add_model(constants.M_DichotomousHill, settings)
        session.add_model(constants.M_Gamma, settings)
        session.add_model(constants.M_Logistic, settings)
        session.add_model(constants.M_LogLogistic, settings)
        session.add_model(constants.M_LogProbit, settings)
        session.add_model(constants.M_Multistage, settings)
        session.add_model(constants.M_Probit, settings)
        session.add_model(constants.M_QuantalLinear, settings)
        session.add_model(constants.M_Weibull, settings)


class ContinuousInputSettings(BaseModel):
    dose_units_id: int
    num_doses_dropped: conint(ge=0) = 0
    bmr_type: ContinuousRiskType = ContinuousRiskType.StandardDeviation
    bmr_value: confloat(gt=0) = 1
    variance_model: DistType = DistType.normal

    def add_models(self, session):
        settings = {
            "bmr_type": self.bmr_type,
            "bmr": self.bmr_value,
            "disttype": self.variance_model,
        }
        session.add_model(constants.M_ExponentialM3, settings)
        session.add_model(constants.M_ExponentialM5, settings)
        session.add_model(constants.M_Hill, settings)
        session.add_model(constants.M_Linear, settings)
        session.add_model(constants.M_Polynomial, settings)
        session.add_model(constants.M_Power, settings)


class BmdInputSettings(BaseModel):
    version: int = Field(default=2, const=True)
    dtype: constants.ModelClass
    settings: DichotomousInputSettings | ContinuousInputSettings

    def add_models(self, session):
        self.settings.add_models(session)

    @classmethod
    def create_default(cls, endpoint: Endpoint) -> "BmdInputSettings":
        dose_units_id = endpoint.get_doses_json(json_encode=False)[0]["id"]
        if endpoint.data_type in [DataType.DICHOTOMOUS, DataType.DICHOTOMOUS_CANCER]:
            return cls(
                dtype=constants.ModelClass.DICHOTOMOUS,
                settings=DichotomousInputSettings(dose_units_id=dose_units_id),
            )
        elif endpoint.data_type in [DataType.CONTINUOUS]:
            return cls(
                dtype=constants.ModelClass.CONTINUOUS,
                settings=ContinuousInputSettings(dose_units_id=dose_units_id),
            )
        else:
            raise ValueError(f"Cannot create default for {endpoint.data_type}")


def get_input_options(dtype: str) -> dict:
    if dtype == DataType.CONTINUOUS:
        return dict(
            dtype=DataType.CONTINUOUS,
            bmr_types=[{"id": v[0], "label": v[1]} for v in ContinuousBmrChoices.choices],
            dist_types=[{"id": v[0], "label": v[1]} for v in ContinuousDistTypeChoices.choices],
        )
    elif dtype in [DataType.DICHOTOMOUS, DataType.DICHOTOMOUS_CANCER]:
        return dict(
            dtype=DataType.DICHOTOMOUS,
            bmr_types=[{"id": v[0], "label": v[1]} for v in DichtomoumsBmrChoices.choices],
        )
    else:
        raise ValueError(f"Unknown data type: {dtype}")


class SelectedModel(BaseModel):
    version: int = Field(default=2, const=True)
    model_index: int = -1
    bmdl: float | None = None
    bmd: float | None = None
    bmdu: float | None = None
    model: str = ""
    bmr: str = ""
    notes: str = ""

    def to_bmd_output(self) -> dict:
        index = None if self.model_index == -1 else self.model_index
        return {"model_index": index, "notes": self.notes}
