import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import pybmds
from django.db.models import IntegerChoices
from pybmds.constants import Dtype, Models, PriorClass
from pydantic import BaseModel, Field

from ..animal.constants import DataType
from ..animal.models import Endpoint


@lru_cache
def bmds2_defaults() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "bmds2.json").read_text())


class DichtomoumsBmrChoices(IntegerChoices):
    Extra = pybmds.DichotomousRiskType.ExtraRisk.value, "Extra Risk"
    Added = pybmds.DichotomousRiskType.AddedRisk.value, "Added Risk"


class ContinuousBmrChoices(IntegerChoices):
    StandardDeviation = pybmds.ContinuousRiskType.StandardDeviation.value, "Standard Deviation"
    RelativeDeviation = pybmds.ContinuousRiskType.RelativeDeviation.value, "Relative Deviation"
    AbsoluteDeviation = pybmds.ContinuousRiskType.AbsoluteDeviation.value, "Absolute Deviation"


class ContinuousDistTypeChoices(IntegerChoices):
    normal = pybmds.ContinuousDistType.normal.value, "Constant"
    normal_ncv = pybmds.ContinuousDistType.normal_ncv.value, "Non-constant"


class DichotomousInputSettings(BaseModel):
    num_doses_dropped: Annotated[int, Field(ge=0)] = 0
    bmr_type: pybmds.DichotomousRiskType = pybmds.DichotomousRiskType.ExtraRisk
    bmr_value: Annotated[float, Field(gt=0)] = 0.1

    def add_models(self, session: pybmds.Session):
        settings = {"bmr_type": self.bmr_type, "bmr": self.bmr_value}
        session.add_model(
            Models.DichotomousHill,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.Gamma,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.Logistic,
            {"priors": PriorClass.frequentist_unrestricted, **settings},
        )
        session.add_model(
            Models.LogLogistic,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.LogProbit,
            {"priors": PriorClass.frequentist_unrestricted, **settings},
        )
        session.add_model(
            Models.Multistage,
            {"priors": PriorClass.frequentist_restricted, "degree": 1, **settings},
        )
        session.add_model(
            Models.Multistage,
            {"priors": PriorClass.frequentist_restricted, "degree": 2, **settings},
        )
        session.add_model(
            Models.Multistage,
            {"priors": PriorClass.frequentist_restricted, "degree": 3, **settings},
        )
        session.add_model(
            Models.Probit,
            {"priors": PriorClass.frequentist_unrestricted, **settings},
        )
        session.add_model(
            Models.QuantalLinear,
            {"priors": PriorClass.frequentist_unrestricted, **settings},
        )
        session.add_model(
            Models.Weibull,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )


class ContinuousInputSettings(BaseModel):
    num_doses_dropped: Annotated[int, Field(ge=0)] = 0
    bmr_type: pybmds.ContinuousRiskType = pybmds.ContinuousRiskType.StandardDeviation
    bmr_value: Annotated[float, Field(gt=0)] = 1
    variance_model: pybmds.ContinuousDistType = pybmds.ContinuousDistType.normal

    def add_models(self, session: pybmds.Session):
        settings = {
            "bmr_type": self.bmr_type,
            "bmr": self.bmr_value,
            "disttype": self.variance_model,
        }
        session.add_model(
            Models.ExponentialM3,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.ExponentialM5,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.Hill,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )
        session.add_model(
            Models.Linear,
            {"priors": PriorClass.frequentist_unrestricted, **settings},
        )
        session.add_model(
            Models.Polynomial,
            {"priors": PriorClass.frequentist_restricted, "degree": 2, **settings},
        )
        session.add_model(
            Models.Polynomial,
            {"priors": PriorClass.frequentist_restricted, "degree": 3, **settings},
        )
        session.add_model(
            Models.Power,
            {"priors": PriorClass.frequentist_restricted, **settings},
        )


class BmdInputSettings(BaseModel):
    version: Literal[2] = 2
    dtype: Dtype
    dose_units_id: int
    settings: Annotated[
        list[DichotomousInputSettings | ContinuousInputSettings], Field(min_length=1)
    ]

    def add_models(self, session):
        self.settings.add_models(session)

    @classmethod
    def create_default(cls, endpoint: Endpoint) -> "BmdInputSettings":
        dose_units_id = endpoint.get_doses_json(json_encode=False)[0]["id"]
        if endpoint.data_type in [DataType.DICHOTOMOUS, DataType.DICHOTOMOUS_CANCER]:
            return cls(
                dtype=Dtype.DICHOTOMOUS,
                dose_units_id=dose_units_id,
                settings=[DichotomousInputSettings()],
            )
        elif endpoint.data_type in [DataType.CONTINUOUS]:
            return cls(
                dtype=Dtype.CONTINUOUS,
                dose_units_id=dose_units_id,
                settings=[ContinuousInputSettings()],
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
    version: Literal[2] = 2
    bmds_model_index: int = Field(-1, alias="model_index")
    bmdl: float | None = None
    bmd: float | None = None
    bmdu: float | None = None
    model: str = ""
    bmr: str = ""
    notes: str = ""

    def to_bmd_output(self) -> dict:
        index = None if self.bmds_model_index == -1 else self.bmds_model_index
        return {"model_index": index, "notes": self.notes}
