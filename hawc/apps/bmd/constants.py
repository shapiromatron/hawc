import json
from functools import lru_cache
from pathlib import Path

from bmds.bmds3.constants import DistType
from bmds.bmds3.types.continuous import ContinuousRiskType
from bmds.bmds3.types.dichotomous import DichotomousRiskType
from django.db import models
from django.db.models import IntegerChoices
from pydantic import BaseModel, confloat, conint

from ..animal.constants import DataType


class BmdsVersion(models.TextChoices):
    BMDS2601 = "BMDS2601", "BMDS 2.6.0.1"
    BMDS270 = "BMDS270", "BMDS 2.7"
    BMDS330 = "BMDS330", "BMDS 3.3 (2022.10)"


@lru_cache()
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


class ContinuousInputSettings(BaseModel):
    dose_units_id: int
    num_doses_dropped: conint(ge=0) = 0
    bmr_type: ContinuousRiskType = ContinuousRiskType.RelativeDeviation
    bmr_value: confloat(gt=0) = 0.1
    variance_model: DistType = DistType.normal


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
